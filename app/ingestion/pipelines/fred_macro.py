from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

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
