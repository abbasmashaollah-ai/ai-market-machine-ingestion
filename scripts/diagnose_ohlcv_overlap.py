from __future__ import annotations

import argparse
import os
from collections import Counter, OrderedDict
from datetime import date

from scripts.persist_fred_macro import _open_connection, load_local_env_if_available


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _use_cursor(connection: object) -> bool:
    return hasattr(connection, "cursor") and not hasattr(connection, "execute")


def _fetch_all(connection: object, sql: str, params: tuple[object, ...] = ()) -> list[dict[str, object]]:
    cursor = None
    try:
        if _use_cursor(connection):
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


def _build_query() -> str:
    return (
        "SELECT symbol, timestamp, timeframe, source, adjusted "
        "FROM canonical_ohlcv "
        "WHERE symbol = %s AND timestamp >= %s AND timestamp <= %s AND timeframe = %s "
        "ORDER BY timestamp ASC, source ASC, adjusted ASC"
    )


def _group_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[tuple[object, object, object], list[dict[str, object]]] = {}
    for row in rows:
        key = (row.get("symbol"), row.get("timestamp"), row.get("timeframe"))
        groups.setdefault(key, []).append(row)
    grouped_rows = []
    for (symbol, timestamp, timeframe), items in groups.items():
        grouped_rows.append(
            {
                "symbol": symbol,
                "timestamp": timestamp,
                "timeframe": timeframe,
                "count": len(items),
                "rows": items,
            }
        )
    grouped_rows.sort(key=lambda item: item["timestamp"])
    return grouped_rows


def _ordered_unique(values: list[object]) -> list[object]:
    return list(OrderedDict.fromkeys(values))


def _format_value(value: object) -> str:
    if hasattr(value, "isoformat"):
        return value.isoformat()  # type: ignore[no-any-return]
    return "None" if value is None else str(value)


def _format_counts(counter: Counter[object]) -> str:
    items = [f"{key}={counter[key]}" for key in sorted(counter, key=lambda value: str(value))]
    return "{" + ", ".join(items) + "}"


def _format_group(group: dict[str, object]) -> str:
    rows = group["rows"]
    sources = _ordered_unique([row.get("source") for row in rows])
    adjusted_values = _ordered_unique([row.get("adjusted") for row in rows])
    return (
        f"timestamp={_format_value(group['timestamp'])} "
        f"count={group['count']} "
        f"sources={sources} "
        f"adjusted_values={adjusted_values}"
    )


def _print_summary(*, symbol: str, timeframe: str, start_date: date, end_date: date, rows: list[dict[str, object]]) -> None:
    groups = _group_rows(rows)
    duplicate_groups = [group for group in groups if int(group["count"]) > 1]
    sources = _ordered_unique([row.get("source") for row in rows])
    adjusted_values = _ordered_unique([row.get("adjusted") for row in rows])
    source_counts: Counter[object] = Counter(row.get("source") for row in rows)
    adjusted_counts: Counter[object] = Counter(row.get("adjusted") for row in rows)
    print(
        f"symbol={symbol} "
        f"timeframe={timeframe} "
        f"start_date={start_date.isoformat()} "
        f"end_date={end_date.isoformat()} "
        f"total_rows={len(rows)} "
        f"unique_timestamp_count={len(groups)} "
        f"duplicate_timestamp_groups={len(duplicate_groups)} "
        f"sources={sources} "
        f"adjusted_values={adjusted_values} "
        f"per_source_row_counts={_format_counts(source_counts)} "
        f"per_adjusted_row_counts={_format_counts(adjusted_counts)}"
    )
    sample_limit = 5
    for index, group in enumerate(duplicate_groups[:sample_limit], start=1):
        print(f"sample_duplicate_group_{index} {_format_group(group)}")
    if len(duplicate_groups) > sample_limit:
        print(f"sample_duplicate_groups_truncated={len(duplicate_groups) - sample_limit}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose overlapping read-only Polygon OHLCV rows in canonical_ohlcv.")
    parser.add_argument("--symbol", required=True, help="Ticker symbol.")
    parser.add_argument("--start-date", required=True, help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", required=True, help="End date in YYYY-MM-DD format.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    args = parser.parse_args()

    load_local_env_if_available()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    connection = None
    try:
        connection = _open_connection(database_url)
        rows = _fetch_all(
            connection,
            _build_query(),
            (args.symbol, _parse_date(args.start_date), _parse_date(args.end_date), args.timeframe),
        )
        _print_summary(
            symbol=args.symbol,
            timeframe=args.timeframe,
            start_date=_parse_date(args.start_date),
            end_date=_parse_date(args.end_date),
            rows=rows,
        )
    finally:
        if connection is not None and hasattr(connection, "close"):
            connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
