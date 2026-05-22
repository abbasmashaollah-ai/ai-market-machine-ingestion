from __future__ import annotations

import argparse
import os
from collections import Counter
from contextlib import closing
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from app.ingestion.pipelines.fred_macro import FredMacroPipelineRequest, plan_fred_macro_fetch_tasks
from app.quality.macro_checks import validate_macro_observation
from app.vendors.common.http import UrlLibHttpClient
from app.vendors.fred.client import FredClientConfig, UnsupportedFredClient
from app.vendors.fred.mapper import fred_observation_to_normalized_macro
from app.vendors.fred.series_catalog import SeriesCategory, get_active_series, get_series_by_category
from app.writers.canonical_writer import WriteStatus
from app.writers.macro_writer import MacroWriter


def load_local_env_if_available() -> bool:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return False
    return bool(load_dotenv())


def select_series_ids(*, series_ids: tuple[str, ...] | None, category: str | None, include_all: bool) -> tuple[str, ...]:
    if series_ids:
        return tuple(series_ids)
    series = get_active_series()
    if category is not None:
        series = get_series_by_category(SeriesCategory(category))
    if include_all:
        return tuple(item.series_id for item in series)
    return tuple(item.series_id for item in series if item.priority == 1)


@dataclass(frozen=True)
class SeriesPersistSummary:
    series_id: str
    rows_fetched: int
    rows_valid: int
    rows_written: int
    validation_failures: int
    failure_reasons: dict[str, int]


def _build_request(series_ids: tuple[str, ...], category: str | None) -> FredMacroPipelineRequest:
    end_date = date.today()
    return FredMacroPipelineRequest(
        series_ids=series_ids,
        start_date=end_date - timedelta(days=5 * 365),
        end_date=end_date,
        category=category,
        dry_run=True,
    )


def _build_fred_client(api_key: str) -> UnsupportedFredClient:
    return UnsupportedFredClient(FredClientConfig(api_key=api_key), http_client=UrlLibHttpClient())


def _load_postgres_connect():
    try:
        from psycopg import connect as psycopg_connect  # type: ignore
    except ImportError:
        try:
            from psycopg2 import connect as psycopg_connect  # type: ignore
        except ImportError as exc:  # pragma: no cover - dependency specific
            raise RuntimeError("PostgreSQL writes require psycopg or psycopg2 to be installed.") from exc
    return psycopg_connect


def _open_connection(database_url: str):
    scheme = database_url.split(":", 1)[0].lower()
    if scheme not in {"postgresql", "postgres"}:
        raise RuntimeError("DATABASE_URL must use postgresql:// or postgres://")
    return _load_postgres_connect()(database_url)


def _extract_observations(payload: dict[str, object]) -> list[dict[str, object]]:
    observations = payload.get("observations")
    if isinstance(observations, list):
        return [row for row in observations if isinstance(row, dict)]
    return []


def _build_valid_rows(series_id: str, observations: list[dict[str, object]]) -> tuple[list[object], int, dict[str, int]]:
    validation_failures = 0
    failure_reasons: Counter[str] = Counter()
    valid_rows: list[object] = []

    for observation in observations:
        enriched_observation = dict(observation)
        enriched_observation["series_id"] = series_id
        if enriched_observation.get("value") == ".":
            enriched_observation["value"] = None
        try:
            normalized = fred_observation_to_normalized_macro(enriched_observation)
            validation_results = validate_macro_observation(normalized)
        except Exception as exc:
            validation_failures += 1
            failure_reasons[exc.__class__.__name__] += 1
            continue

        failed_results = [result for result in validation_results if not result.passed]
        validation_failures += len(failed_results)
        for failed_result in failed_results:
            failure_reasons[failed_result.check_name] += 1
        if not failed_results:
            valid_rows.append(normalized)

    return valid_rows, validation_failures, dict(failure_reasons)


def build_series_summaries(
    *,
    selected_series_ids: tuple[str, ...],
    fred_client: UnsupportedFredClient,
    writer: MacroWriter | None,
) -> list[SeriesPersistSummary]:
    request = _build_request(selected_series_ids, None)
    tasks = plan_fred_macro_fetch_tasks(request)
    summaries: list[SeriesPersistSummary] = []

    for task in tasks:
        payload = fred_client.fetch_series_observations_raw(
            task.series_id,
            observation_start=request.start_date.isoformat(),
            observation_end=request.end_date.isoformat(),
        )
        observations = _extract_observations(payload)
        valid_rows, validation_failures, failure_reasons = _build_valid_rows(task.series_id, observations)
        rows_written = 0
        if writer is not None and valid_rows:
            write_result = writer.write(valid_rows)
            rows_written = write_result.written_count
        summaries.append(
            SeriesPersistSummary(
                series_id=task.series_id,
                rows_fetched=len(observations),
                rows_valid=len(valid_rows),
                rows_written=rows_written,
                validation_failures=validation_failures,
                failure_reasons=failure_reasons,
            )
        )

    return summaries


def _print_summaries(summaries: list[SeriesPersistSummary]) -> None:
    for summary in summaries:
        print(
            f"series_id={summary.series_id} "
            f"rows_fetched={summary.rows_fetched} "
            f"rows_valid={summary.rows_valid} "
            f"rows_written={summary.rows_written} "
            f"validation_failures={summary.validation_failures} "
            f"failure_reasons={summary.failure_reasons}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Persist normalized FRED macro data into macro_rate_observations.")
    parser.add_argument("--series-id", nargs="*", help="Specific FRED series IDs to persist.")
    parser.add_argument("--category", help="Persist a single category.")
    parser.add_argument("--all", action="store_true", help="Persist all active catalog series.")
    parser.add_argument("--confirm-write", action="store_true", help="Actually write valid rows.")
    args = parser.parse_args()

    load_local_env_if_available()
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise RuntimeError("FRED_API_KEY is required")
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    selected_series_ids = select_series_ids(
        series_ids=tuple(args.series_id) if args.series_id else None,
        category=args.category,
        include_all=args.all,
    )
    fred_client = _build_fred_client(api_key)
    writer = None
    connection = None
    try:
        if args.confirm_write:
            connection = _open_connection(database_url)
            writer = MacroWriter(connection)
        summaries = build_series_summaries(
            selected_series_ids=selected_series_ids,
            fred_client=fred_client,
            writer=writer,
        )
        _print_summaries(summaries)
    finally:
        if connection is not None and hasattr(connection, "close"):
            connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
