from __future__ import annotations

import argparse
import os
from collections import Counter, defaultdict

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


def _build_filters(*, vendor: str | None, exchange: str | None, asset_type: str | None, active: bool | None) -> tuple[str, tuple[object, ...]]:
    clauses: list[str] = []
    params: list[object] = []
    if vendor is not None:
        clauses.append("vendor = %s")
        params.append(vendor)
    if exchange is not None:
        clauses.append("exchange = %s")
        params.append(exchange)
    if asset_type is not None:
        clauses.append("asset_type = %s")
        params.append(asset_type)
    if active is True:
        clauses.append("active IS TRUE")
    elif active is False:
        clauses.append("active IS FALSE")
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    return where, tuple(params)


def _coverage_status(
    *,
    total_rows: int,
    active_rows: int,
    inactive_rows: int,
    missing_exchange_count: int,
    missing_asset_type_count: int,
    duplicate_symbol_count: int,
    min_total: int,
    min_active: int,
    max_missing_exchange_ratio: float,
    max_missing_asset_type_ratio: float,
) -> str:
    if total_rows < min_total or active_rows < min_active or total_rows == 0:
        return "FAIL"
    if (missing_exchange_count / total_rows) > max_missing_exchange_ratio:
        return "FAIL"
    if (missing_asset_type_count / total_rows) > max_missing_asset_type_ratio:
        return "FAIL"
    if inactive_rows > 0 or duplicate_symbol_count > 0 or missing_exchange_count > 0 or missing_asset_type_count > 0:
        return "WARN"
    return "PASS"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Assess symbol master coverage read-only.")
    parser.add_argument("--vendor")
    parser.add_argument("--exchange")
    parser.add_argument("--asset-type")
    parser.add_argument("--active", choices=("true", "false"))
    parser.add_argument("--min-total", type=int, default=1)
    parser.add_argument("--min-active", type=int, default=1)
    parser.add_argument("--max-missing-exchange-ratio", type=float, default=0.05)
    parser.add_argument("--max-missing-asset-type-ratio", type=float, default=0.05)
    args = parser.parse_args(argv)

    load_local_env_if_available()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    active = None if args.active is None else args.active == "true"
    where_clause, params = _build_filters(vendor=args.vendor, exchange=args.exchange, asset_type=args.asset_type, active=active)
    connection = _open_connection(database_url)
    try:
        rows = _fetch_all(
            connection,
            f"""
            SELECT vendor, exchange, asset_type, active, vendor_symbol, symbol
            FROM public.symbol_master
            {where_clause}
            """.strip(),
            params,
        )
        total_rows = len(rows)
        active_rows = sum(1 for row in rows if row.get("active") is True)
        inactive_rows = sum(1 for row in rows if row.get("active") is False)
        by_exchange = Counter(str(row.get("exchange") or "missing") for row in rows)
        by_asset_type = Counter(str(row.get("asset_type") or "missing") for row in rows)
        missing_vendor_symbol_count = sum(1 for row in rows if not row.get("vendor_symbol"))
        missing_exchange_count = sum(1 for row in rows if not row.get("exchange"))
        missing_asset_type_count = sum(1 for row in rows if not row.get("asset_type"))
        symbol_counts = Counter(str(row.get("symbol") or "") for row in rows if row.get("symbol"))
        duplicate_symbol_count = sum(count - 1 for count in symbol_counts.values() if count > 1)
        coverage_status = _coverage_status(
            total_rows=total_rows,
            active_rows=active_rows,
            inactive_rows=inactive_rows,
            missing_exchange_count=missing_exchange_count,
            missing_asset_type_count=missing_asset_type_count,
            duplicate_symbol_count=duplicate_symbol_count,
            min_total=args.min_total,
            min_active=args.min_active,
            max_missing_exchange_ratio=args.max_missing_exchange_ratio,
            max_missing_asset_type_ratio=args.max_missing_asset_type_ratio,
        )
        print(
            f"coverage_status={coverage_status} "
            f"total_rows={total_rows} "
            f"active_rows={active_rows} "
            f"inactive_rows={inactive_rows} "
            f"missing_vendor_symbol_count={missing_vendor_symbol_count} "
            f"missing_exchange_count={missing_exchange_count} "
            f"missing_asset_type_count={missing_asset_type_count} "
            f"duplicate_symbol_count={duplicate_symbol_count} "
            f"by_exchange={dict(by_exchange)} "
            f"by_asset_type={dict(by_asset_type)} "
            f"vendor={args.vendor if args.vendor else None} "
            f"exchange={args.exchange if args.exchange else None} "
            f"asset_type={args.asset_type if args.asset_type else None} "
            f"active={args.active if args.active else None}"
        )
    finally:
        if hasattr(connection, "close"):
            connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
