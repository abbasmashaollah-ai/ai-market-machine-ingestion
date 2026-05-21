from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from app.vendors.fred.series_catalog import (
    FREDSeriesDefinition,
    SERIES_CATALOG,
    SeriesCategory,
    get_active_series,
    get_series_by_category,
)
from scripts.probe_fred_series import (
    build_default_five_year_window,
    extract_observation_rows,
    extract_safe_debug_details,
    load_local_env_if_available,
    run_probe_details,
)


@dataclass(frozen=True)
class CatalogProbeSummary:
    series_id: str
    category: str
    row_count: int
    first_date: str | None
    last_date: str | None
    status_code: int


def format_summary_line(summary: CatalogProbeSummary) -> str:
    return (
        f"series_id={summary.series_id} category={summary.category} "
        f"row_count={summary.row_count} first_date={summary.first_date} "
        f"last_date={summary.last_date} status_code={summary.status_code}"
    )


def format_debug_safe_line(result: object, summary: CatalogProbeSummary) -> str:
    debug_details = extract_safe_debug_details(result.payload)
    request_params = {k: v for k, v in result.request_metadata.query_params.items() if k != "api_key"}
    observations_count = len(extract_observation_rows(result.response.parsed_json))
    return (
        f"series_id={summary.series_id} "
        f"status_code={summary.status_code} "
        f"raw_text_length={result.response.raw_text_length} "
        f"response_keys={debug_details['response_keys']} "
        f"observations_count={observations_count} "
        f"fred_error={debug_details['fred_error']} "
        f"request_params={request_params}"
    )


def select_catalog_series(*, include_all: bool = False, category: str | None = None) -> tuple[FREDSeriesDefinition, ...]:
    series = get_active_series()
    if category is not None:
        series = get_series_by_category(SeriesCategory(category))
    if include_all:
        return series
    return tuple(item for item in series if item.priority == 1)


def summarize_catalog_results(results: list[object]) -> list[CatalogProbeSummary]:
    summaries: list[CatalogProbeSummary] = []
    for result in results:
        summary = result.summary
        series = next(item for item in SERIES_CATALOG if item.series_id == summary.series_id)
        summaries.append(
            CatalogProbeSummary(
                series_id=summary.series_id,
                category=series.category.value,
                row_count=summary.row_count,
                first_date=summary.first_date,
                last_date=summary.last_date,
                status_code=result.response.status_code,
            )
        )
    return summaries


def _write_output(path: str, summaries: list[CatalogProbeSummary]) -> None:
    payload = [summary.__dict__ for summary in summaries]
    Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe the active FRED macro catalog.")
    parser.add_argument("--all", action="store_true", help="Probe all active series instead of only priority 1.")
    parser.add_argument("--category", help="Probe a single category.")
    parser.add_argument("--output", help="Optional JSON output path.")
    parser.add_argument("--debug-safe", action="store_true", help="Print safe debug details when a series has no rows.")
    args = parser.parse_args()

    load_local_env_if_available()
    selected_series = select_catalog_series(include_all=args.all, category=args.category)
    observation_start, observation_end = build_default_five_year_window()
    results = run_probe_details(
        series_ids=tuple(series.series_id for series in selected_series),
        observation_start=observation_start,
        observation_end=observation_end,
    )
    summaries = summarize_catalog_results(results)

    for result, summary in zip(results, summaries, strict=True):
        print(format_summary_line(summary))
        if args.debug_safe and summary.row_count == 0:
            print(format_debug_safe_line(result, summary))

    if args.output:
        _write_output(args.output, summaries)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
