from __future__ import annotations

import argparse
import os
import time
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


def _is_rate_limit_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return "429" in message or "rate limit" in message or "too many requests" in message


def _emit(summary: dict[str, object]) -> None:
    for key in ("requested_count", "found_count", "missing_count", "failed_count", "valid_count", "invalid_count", "rows_written", "rate_limit_detected"):
        print(f"{key}={summary.get(key)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch targeted Polygon symbol-master details for ETF/index candidates.")
    parser.add_argument("--symbol", action="append", help="Repeatable explicit symbol list.")
    parser.add_argument("--from-etf-index-candidates", action="store_true", help="Use the deterministic ETF/index candidate list.")
    parser.add_argument("--live-check", action="store_true", help="Require POLYGON_API_KEY and fetch live Polygon symbol details.")
    parser.add_argument("--confirm-write", action="store_true", help="Require DATABASE_URL and write valid normalized rows through SymbolMasterWriter.")
    parser.add_argument("--sleep-seconds-between-symbols", type=float, default=0.0, help="Sleep between symbol lookups.")
    parser.add_argument("--stop-on-rate-limit", dest="stop_on_rate_limit", action="store_true", default=True, help="Stop safely on the first rate-limit response.")
    parser.add_argument("--no-stop-on-rate-limit", dest="stop_on_rate_limit", action="store_false", help="Continue until max-rate-limit-failures is reached.")
    parser.add_argument("--max-rate-limit-failures", type=int, default=1, help="Maximum tolerated rate-limit failures when continuing.")
    args = parser.parse_args(argv)

    if args.live_check and not os.getenv("POLYGON_API_KEY"):
        raise RuntimeError("POLYGON_API_KEY is required for --live-check")
    if args.confirm_write and not args.live_check:
        raise RuntimeError("--confirm-write requires --live-check")
    if args.confirm_write and not os.getenv("DATABASE_URL"):
        raise RuntimeError("DATABASE_URL is required when --confirm-write is used")
    if args.max_rate_limit_failures < 0:
        raise RuntimeError("--max-rate-limit-failures must be >= 0")

    requested_symbols = list(args.symbol or [])
    if args.from_etf_index_candidates:
        requested_symbols.extend(_candidate_symbols())
    requested_symbols = list(dict.fromkeys(requested_symbols))
    if not requested_symbols:
        raise RuntimeError("provide at least one --symbol or use --from-etf-index-candidates")

    adapter = _build_adapter(live_check=args.live_check)
    payloads: list[dict[str, object]] = []
    found_symbols: set[str] = set()
    failed_count = 0
    rate_limit_detected = False

    if args.live_check:
        rate_limit_failures = 0
        for index, symbol in enumerate(requested_symbols):
            try:
                payload = adapter.fetch_reference_ticker_raw(symbol)
            except Exception as exc:
                if _is_rate_limit_error(exc):
                    rate_limit_detected = True
                    rate_limit_failures += 1
                    if args.stop_on_rate_limit or rate_limit_failures > args.max_rate_limit_failures:
                        break
                    failed_count += 1
                    continue
                failed_count += 1
                continue
            if payload:
                payloads.append(payload)
                ticker = payload.get("ticker")
                if ticker:
                    found_symbols.add(str(ticker))
            else:
                failed_count += 1
            if args.sleep_seconds_between_symbols > 0 and index < len(requested_symbols) - 1:
                time.sleep(args.sleep_seconds_between_symbols)
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
    invalid_records = [record for record in records if validate_symbol_record(record)]
    missing_count = len(requested_symbols) - len(found_symbols)
    summary: dict[str, object] = {
        "requested_count": len(requested_symbols),
        "found_count": len(found_symbols),
        "missing_count": missing_count,
        "failed_count": failed_count,
        "valid_count": len(valid_records),
        "invalid_count": len(invalid_records),
        "rows_written": 0,
        "rate_limit_detected": rate_limit_detected,
    }

    if args.confirm_write and valid_records:
        database_url = os.getenv("DATABASE_URL")
        with closing(_open_connection(database_url)) as connection:
            writer = SymbolMasterWriter(connection)
            write_result = writer.write(valid_records)
        summary["rows_written"] = write_result.written_count

    _emit(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
