from __future__ import annotations

import argparse
import os
from collections import defaultdict
from contextlib import closing
from datetime import date

from app.normalization.fred_macro import get_starter_fred_macro_series
from scripts.persist_fred_macro import _open_connection, load_local_env_if_available


def _fetch_all(connection: object, sql: str, params: tuple[object, ...] = ()) -> list[dict[str, object]]:
    cursor = None
    try:
        if hasattr(connection, "cursor") and not hasattr(connection, "execute"):
            cursor = connection.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
        else:
            result = connection.execute(sql, params)  # type: ignore[call-arg]
            rows = result.fetchall() if hasattr(result, "fetchall") else []
        if not rows:
            return []
        first = rows[0]
        if isinstance(first, dict):
            return [row for row in rows if isinstance(row, dict)]
        columns = [desc[0] for desc in getattr(cursor, "description", [])] if cursor is not None else []
        return [dict(zip(columns, row)) for row in rows]
    finally:
        if cursor is not None and hasattr(cursor, "close"):
            cursor.close()


def _parse_date(value: object) -> date | None:
    if isinstance(value, date):
        return value
    if isinstance(value, str) and value:
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None


def _starter_series() -> tuple[str, ...]:
    return tuple(series.series_id for series in get_starter_fred_macro_series())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify FRED macro evidence chain safely.")
    parser.add_argument("--series", action="append", help="Optional series to check; defaults to starter series.")
    args = parser.parse_args(argv)

    load_local_env_if_available()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    requested_series = tuple(s.upper() for s in args.series) if args.series else _starter_series()
    connection = _open_connection(database_url)
    try:
        rows = _fetch_all(
            connection,
            """
            SELECT series_id, observation_date, value, source
            FROM public.macro_rate_observations
            WHERE source = %s
            """.strip(),
            ("fred",),
        )
        row_count_by_series: dict[str, int] = defaultdict(int)
        latest_observation_dates: dict[str, str | None] = {series_id: None for series_id in requested_series}
        missing_value_count = 0
        for row in rows:
            series_id = str(row.get("series_id") or "")
            if not series_id:
                continue
            row_count_by_series[series_id] += 1
            if row.get("value") is None:
                missing_value_count += 1
            observation_date = _parse_date(row.get("observation_date"))
            if observation_date is not None:
                current = latest_observation_dates.get(series_id)
                if current is None or observation_date.isoformat() > current:
                    latest_observation_dates[series_id] = observation_date.isoformat()
        missing_series = [series_id for series_id in requested_series if row_count_by_series.get(series_id, 0) == 0]
        total_rows = len(rows)
        if total_rows == 0:
            evidence_status = "FAIL"
        elif missing_series:
            evidence_status = "WARN"
        else:
            evidence_status = "PASS"
        print(
            f"series_count={len(requested_series)} "
            f"total_rows={total_rows} "
            f"row_count_by_series={dict(row_count_by_series)} "
            f"latest_observation_dates={latest_observation_dates} "
            f"missing_series={missing_series} "
            f"missing_value_count={missing_value_count} "
            f"evidence_status={evidence_status}"
        )
    finally:
        if hasattr(connection, "close"):
            connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
