from __future__ import annotations

import argparse
import os

from app.normalization.etf_index_universe import build_etf_index_universe_candidates, summarize_candidate_groups
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


def _emit(summary: dict[str, object]) -> None:
    for key in ("candidate_count", "found_count", "missing_count", "no_vendor_calls", "no_db_writes"):
        print(f"{key}={summary.get(key)}")
    print(f"group_counts={summary.get('group_counts')}")
    if summary.get("show_found"):
        print(f"found_symbols={summary.get('found_symbols')}")
    if summary.get("show_missing"):
        print(f"missing_symbols={summary.get('missing_symbols')}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run ETF/index universe expansion planning.")
    parser.add_argument("--check-symbol-master", action="store_true", help="Validate candidates against public.symbol_master.")
    parser.add_argument("--vendor", default="polygon", help="Expected vendor in symbol_master, default polygon.")
    parser.add_argument("--show-missing", action="store_true", help="Print missing symbols as a safe list.")
    parser.add_argument("--show-found", action="store_true", help="Print found symbols as a safe list.")
    args = parser.parse_args(argv)

    candidates = build_etf_index_universe_candidates()
    summary: dict[str, object] = {
        "candidate_count": len(candidates),
        "found_count": 0,
        "missing_count": len(candidates),
        "group_counts": summarize_candidate_groups(candidates),
        "no_vendor_calls": True,
        "no_db_writes": True,
        "show_found": args.show_found,
        "show_missing": args.show_missing,
        "found_symbols": [],
        "missing_symbols": [candidate.symbol for candidate in candidates],
    }

    if args.check_symbol_master:
        load_local_env_if_available()
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL is required when --check-symbol-master is used")
        connection = _open_connection(database_url)
        try:
            rows = _fetch_all(
                connection,
                """
                SELECT symbol
                FROM public.symbol_master
                WHERE vendor = %s
                """.strip(),
                (args.vendor,),
            )
            found_symbols = {str(row.get("symbol")) for row in rows if row.get("symbol")}
            found_count = sum(1 for candidate in candidates if candidate.symbol in found_symbols)
            summary["found_symbols"] = [candidate.symbol for candidate in candidates if candidate.symbol in found_symbols]
            summary["missing_symbols"] = [candidate.symbol for candidate in candidates if candidate.symbol not in found_symbols]
            summary["found_count"] = found_count
            summary["missing_count"] = len(candidates) - found_count
        finally:
            if hasattr(connection, "close"):
                connection.close()

    _emit(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
