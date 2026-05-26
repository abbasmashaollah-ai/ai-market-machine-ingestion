from __future__ import annotations

import argparse
import os
from contextlib import closing

from app.normalization.etf_index_universe import build_etf_index_universe_candidates
from app.normalization.symbol_master import validate_symbol_record
from app.vendors.polygon_symbol_master import PolygonSymbolMasterAdapter, PolygonSymbolMasterSourceConfig
from app.writers.symbol_master_writer import SymbolMasterWriter
from scripts.persist_fred_macro import _open_connection, load_local_env_if_available


def _build_adapter(*, live_check: bool) -> PolygonSymbolMasterAdapter:
    return PolygonSymbolMasterAdapter(
        PolygonSymbolMasterSourceConfig(api_key=os.getenv("POLYGON_API_KEY") if live_check else None)
    )


def _candidate_symbols() -> list[str]:
    return [candidate.symbol for candidate in build_etf_index_universe_candidates()]


def _emit(summary: dict[str, object]) -> None:
    for key in ("requested_count", "found_count", "missing_count", "valid_count", "invalid_count", "rows_written"):
        print(f"{key}={summary.get(key)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch targeted Polygon symbol-master details for ETF/index candidates.")
    parser.add_argument("--symbol", action="append", help="Repeatable explicit symbol list.")
    parser.add_argument("--from-etf-index-candidates", action="store_true", help="Use the deterministic ETF/index candidate list.")
    parser.add_argument("--live-check", action="store_true", help="Require POLYGON_API_KEY and fetch live Polygon symbol details.")
    parser.add_argument("--confirm-write", action="store_true", help="Require DATABASE_URL and write valid normalized rows through SymbolMasterWriter.")
    args = parser.parse_args(argv)

    if args.live_check and not os.getenv("POLYGON_API_KEY"):
        raise RuntimeError("POLYGON_API_KEY is required for --live-check")
    if args.confirm_write and not args.live_check:
        raise RuntimeError("--confirm-write requires --live-check")
    if args.confirm_write and not os.getenv("DATABASE_URL"):
        raise RuntimeError("DATABASE_URL is required when --confirm-write is used")

    requested_symbols = list(args.symbol or [])
    if args.from_etf_index_candidates:
        requested_symbols.extend(_candidate_symbols())
    requested_symbols = list(dict.fromkeys(requested_symbols))
    if not requested_symbols:
        raise RuntimeError("provide at least one --symbol or use --from-etf-index-candidates")

    adapter = _build_adapter(live_check=args.live_check)
    payloads: list[dict[str, object]] = []
    found_symbols: set[str] = set()
    if args.live_check:
        for symbol in requested_symbols:
            payload = adapter.fetch_reference_ticker_raw(symbol)
            if payload:
                payloads.append(payload)
                if payload.get("ticker"):
                    found_symbols.add(str(payload.get("ticker")))
    else:
        payloads = [
            {
                "ticker": symbol,
                "name": symbol,
                "active": True,
                "delisted": False,
                "primary_exchange": None,
                "type": "ETF" if symbol in {"SPY", "QQQ", "IWM", "DIA"} else "INDEX" if symbol in {"SPX", "NDX", "RUT", "DJI"} else "ETF",
                "currency": "USD",
            }
            for symbol in requested_symbols
        ]
        found_symbols.update(requested_symbols)

    records = [adapter.map_reference_ticker(payload) for payload in payloads]
    valid_records = [record for record in records if not validate_symbol_record(record)]
    missing_count = len(requested_symbols) - len(found_symbols)
    summary: dict[str, object] = {
        "requested_count": len(requested_symbols),
        "found_count": len(found_symbols),
        "missing_count": missing_count,
        "valid_count": len(valid_records),
        "invalid_count": len(records) - len(valid_records),
        "rows_written": 0,
    }

    if args.confirm_write:
        database_url = os.getenv("DATABASE_URL")
        with closing(_open_connection(database_url)) as connection:
            writer = SymbolMasterWriter(connection)
            write_result = writer.write(valid_records)
        summary["rows_written"] = write_result.written_count

    _emit(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
