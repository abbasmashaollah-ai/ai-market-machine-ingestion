from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from app.models.normalized import NormalizedMacroObservation
from app.normalization.common import safe_text
from app.quality.macro_checks import validate_macro_observation
from app.vendors.fred.client import FredClient
from app.vendors.fred.mapper import fred_observation_to_normalized_macro
from app.vendors.fred.series_catalog import FREDSeriesDefinition, SeriesCategory, get_series_definition


@dataclass(frozen=True)
class FredMacroPipelineRequest:
    series_ids: tuple[str, ...]
    start_date: date
    end_date: date
    category: SeriesCategory | str | None = None
    priority: int | None = None
    dry_run: bool = True


@dataclass(frozen=True)
class PlannedFredMacroFetchTask:
    series_id: str
    category: str
    start_date: date
    end_date: date
    vendor: str = "fred"
    dataset: str = "macro_observations"


@dataclass(frozen=True)
class FredMacroDryRunResult:
    series_id: str
    rows_fetched: int
    rows_normalized: int
    validation_failures: int
    validation_failure_reasons: dict[str, int] = field(default_factory=dict)
    sample_failed_dates: tuple[str, ...] = field(default_factory=tuple)
    sample_failed_values: tuple[str, ...] = field(default_factory=tuple)
    first_date: str | None = None
    last_date: str | None = None


def _resolve_series(series_id: str) -> FREDSeriesDefinition:
    series = get_series_definition(series_id)
    if series is None:
        raise ValueError(f"Unknown FRED series_id: {series_id}")
    return series


def plan_fred_macro_fetch_tasks(request: FredMacroPipelineRequest) -> tuple[PlannedFredMacroFetchTask, ...]:
    selected_series = tuple(_resolve_series(series_id) for series_id in request.series_ids)
    if request.category is not None:
        category_value = SeriesCategory(request.category)
        selected_series = tuple(series for series in selected_series if series.category == category_value)
    if request.priority is not None:
        selected_series = tuple(series for series in selected_series if series.priority == request.priority)
    return tuple(
        PlannedFredMacroFetchTask(
            series_id=series.series_id,
            category=series.category.value,
            start_date=request.start_date,
            end_date=request.end_date,
        )
        for series in selected_series
    )


def _extract_observations(payload: dict[str, object]) -> list[dict[str, object]]:
    observations = payload.get("observations")
    if isinstance(observations, list):
        return [row for row in observations if isinstance(row, dict)]
    return []


def _normalize_raw_value(value: object) -> object | None:
    if value == ".":
        return None
    return value


def execute_fred_macro_dry_run(
    request: FredMacroPipelineRequest,
    fred_client: FredClient,
) -> tuple[FredMacroDryRunResult, ...]:
    tasks = plan_fred_macro_fetch_tasks(request)
    results: list[FredMacroDryRunResult] = []
    for task in tasks:
        payload = fred_client.fetch_series_observations_raw(
            task.series_id,
            observation_start=request.start_date.isoformat(),
            observation_end=request.end_date.isoformat(),
        )
        observations = _extract_observations(payload)
        normalized_rows: list[NormalizedMacroObservation] = []
        validation_failures = 0
        validation_failure_reasons: dict[str, int] = {}
        sample_failed_dates: list[str] = []
        sample_failed_values: list[str] = []
        for observation in observations:
            enriched_observation = dict(observation)
            enriched_observation["series_id"] = task.series_id
            enriched_observation["value"] = _normalize_raw_value(enriched_observation.get("value"))
            normalized = fred_observation_to_normalized_macro(enriched_observation)
            normalized_rows.append(normalized)
            validation_results = validate_macro_observation(normalized)
            failed_results = [result for result in validation_results if not result.passed]
            validation_failures += len(failed_results)
            for failed_result in failed_results:
                validation_failure_reasons[failed_result.check_name] = validation_failure_reasons.get(failed_result.check_name, 0) + 1
            if failed_results:
                date_value = safe_text(observation.get("date"))
                raw_value = observation.get("value")
                if date_value is not None:
                    sample_failed_dates.append(date_value)
                if raw_value is not None:
                    sample_failed_values.append(str(raw_value))
        dates = [safe_text(row.get("date")) for row in observations if safe_text(row.get("date"))]
        results.append(
            FredMacroDryRunResult(
                series_id=task.series_id,
                rows_fetched=len(observations),
                rows_normalized=len(normalized_rows),
                validation_failures=validation_failures,
                validation_failure_reasons=validation_failure_reasons,
                sample_failed_dates=tuple(sample_failed_dates[:5]),
                sample_failed_values=tuple(sample_failed_values[:5]),
                first_date=dates[0] if dates else None,
                last_date=dates[-1] if dates else None,
            )
        )
    return tuple(results)
