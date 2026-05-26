from __future__ import annotations

import argparse
import os

from scripts.evidence_chain_helpers import status_from_requirement
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify the symbol master evidence chain safely.")
    parser.add_argument("--symbol", help="Optional canonical symbol to check.")
    args = parser.parse_args(argv)

    load_local_env_if_available()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    connection = _open_connection(database_url)
    try:
        counts = _fetch_all(
            connection,
            """
            SELECT
                COUNT(*) AS row_count,
                COUNT(*) FILTER (WHERE active IS TRUE) AS active_count,
                COUNT(*) FILTER (WHERE active IS FALSE) AS inactive_count
            FROM public.symbol_master
            """.strip(),
        )
        count_row = counts[0] if counts else {"row_count": 0, "active_count": 0, "inactive_count": 0}
        row_count = int(count_row.get("row_count") or 0)
        active_count = int(count_row.get("active_count") or 0)
        inactive_count = int(count_row.get("inactive_count") or 0)
        symbol_found = None
        symbol_status = "PASS"
        if args.symbol:
            rows = _fetch_all(
                connection,
                """
                SELECT symbol, vendor, vendor_symbol, active, exchange, asset_type, name, currency
                FROM public.symbol_master
                WHERE symbol = %s
                LIMIT 1
                """.strip(),
                (args.symbol,),
            )
            symbol_found = bool(rows)
            symbol_status = status_from_requirement(required=True, present=symbol_found)
        evidence_status = "WARN" if row_count == 0 else "PASS"
        if args.symbol and not symbol_found:
            evidence_status = "FAIL"
        print(
            f"row_count={row_count} "
            f"active_count={active_count} "
            f"inactive_count={inactive_count} "
            f"symbol={args.symbol if args.symbol else None} "
            f"symbol_found={symbol_found} "
            f"symbol_status={symbol_status} "
            f"evidence_status={evidence_status}"
        )
    finally:
        if hasattr(connection, "close"):
            connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
