from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict
from datetime import date, timedelta
from pathlib import Path

from app.ingestion.pipelines.fred_macro import FredMacroPipelineRequest, execute_fred_macro_dry_run
from app.vendors.common.http import UrlLibHttpClient
from app.vendors.fred.client import FredClientConfig, UnsupportedFredClient
from app.vendors.fred.series_catalog import SeriesCategory, get_active_series, get_series_by_category


def load_local_env_if_available() -> bool:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return False
    return bool(load_dotenv())


def select_series_ids(*, series_ids: tuple[str, ...] | None, category: str | None, include_all: bool) -> tuple[str, ...]:
    if series_ids:
        return series_ids
    series = get_active_series()
    if category is not None:
        series = get_series_by_category(SeriesCategory(category))
    if include_all:
        return tuple(item.series_id for item in series)
    return tuple(item.series_id for item in series if item.priority == 1)


def _build_request(series_ids: tuple[str, ...], category: str | None, include_all: bool) -> FredMacroPipelineRequest:
    end_date = date.today()
    return FredMacroPipelineRequest(
        series_ids=series_ids,
        start_date=end_date - timedelta(days=5 * 365),
        end_date=end_date,
        category=category,
        dry_run=True,
    )


def _write_output(path: str, summaries: list[dict[str, object]]) -> None:
    Path(path).write_text(json.dumps(summaries, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe the FRED macro dry-run executor.")
    parser.add_argument("--series-id", nargs="*", help="Specific FRED series IDs to probe.")
    parser.add_argument("--category", help="Probe a single category.")
    parser.add_argument("--all", action="store_true", help="Probe all active catalog series.")
    parser.add_argument("--output", help="Optional JSON output path.")
    args = parser.parse_args()

    load_local_env_if_available()
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise RuntimeError("FRED_API_KEY is required")

    selected_series_ids = select_series_ids(
        series_ids=tuple(args.series_id) if args.series_id else None,
        category=args.category,
        include_all=args.all,
    )
    request = _build_request(selected_series_ids, args.category, args.all)
    fred_client = UnsupportedFredClient(FredClientConfig(api_key=api_key), http_client=UrlLibHttpClient())
    results = execute_fred_macro_dry_run(request, fred_client)

    for result in results:
        print(
            f"series_id={result.series_id} rows_fetched={result.rows_fetched} "
            f"rows_normalized={result.rows_normalized} validation_failures={result.validation_failures} "
            f"failure_reasons={result.validation_failure_reasons} "
            f"first_date={result.first_date} last_date={result.last_date}"
        )

    if args.output:
        _write_output(args.output, [asdict(result) for result in results])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
