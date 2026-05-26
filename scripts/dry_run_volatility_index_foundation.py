from __future__ import annotations

import argparse
import os
import time
from dataclasses import dataclass
from datetime import date

from app.normalization.volatility_index import (
    NormalizedVolatilityIndexRecord,
    STARTER_VOLATILITY_INDEX_SYMBOLS,
    normalize_volatility_index_record,
    validate_volatility_index_record,
)
from app.vendors.common.errors import VendorRateLimitedError
from app.vendors.polygon_volatility_index import PolygonVolatilityIndexAdapter, PolygonVolatilityIndexSourceConfig


DEFAULT_SAMPLE_RECORDS: tuple[dict[str, object], ...] = (
    {"symbol": "VIX", "observation_date": "2026-05-21", "value": 18.2, "source": "sample_fixture", "vendor_symbol": "I:VIX", "unit": "index", "notes": "deterministic fixture"},
    {"symbol": "VVIX", "observation_date": "2026-05-21", "value": 92.1, "source": "sample_fixture", "vendor_symbol": "I:VVIX", "unit": "index", "notes": "deterministic fixture"},
    {"symbol": "VXN", "observation_date": "2026-05-21", "value": 21.7, "source": "sample_fixture", "vendor_symbol": "I:VXN", "unit": "index", "notes": "deterministic fixture"},
    {"symbol": "RVX", "observation_date": "2026-05-21", "value": 25.4, "source": "sample_fixture", "vendor_symbol": "I:RVX", "unit": "index", "notes": "deterministic fixture"},
)


@dataclass(frozen=True)
class VolatilityDryRunResult:
    requested_symbols: list[str]
    normalized_records: tuple[NormalizedVolatilityIndexRecord, ...]
    invalid_records: tuple[dict[str, object], ...]
    latest_observation_dates: dict[str, str | None]
    rate_limit_detected: bool
    no_vendor_calls: bool
    no_db_writes: bool


def _build_summary(source_records: tuple[dict[str, object], ...]) -> VolatilityDryRunResult:
    normalized_records = tuple(normalize_volatility_index_record(record) for record in source_records)
    invalid_records = tuple(
        {"record": record, "errors": validate_volatility_index_record(record)}
        for record in normalized_records
        if validate_volatility_index_record(record)
    )
    latest_observation_dates = {
        record.symbol or "unknown": record.observation_date.isoformat() if record.observation_date else None
        for record in normalized_records
    }
    return VolatilityDryRunResult(
        requested_symbols=list(STARTER_VOLATILITY_INDEX_SYMBOLS),
        normalized_records=normalized_records,
        invalid_records=invalid_records,
        latest_observation_dates=latest_observation_dates,
        rate_limit_detected=False,
        no_vendor_calls=True,
        no_db_writes=True,
    )


def _sanitize_vendor_error(message: str) -> str:
    sanitized = message
    for needle in ("POLYGON_API_KEY", "apiKey", "api key", "api-key"):
        sanitized = sanitized.replace(needle, "polygon api key")
    return sanitized


def _normalize_live_records(
    *,
    adapter: PolygonVolatilityIndexAdapter,
    requested_symbols: list[str],
    max_observations: int | None,
    stop_on_rate_limit: bool,
    max_rate_limit_failures: int,
    sleep_seconds_between_symbols: float,
) -> tuple[tuple[NormalizedVolatilityIndexRecord, ...], dict[str, str | None], bool, list[dict[str, object]]]:
    normalized_records: list[NormalizedVolatilityIndexRecord] = []
    latest_observation_dates: dict[str, str | None] = {}
    invalid_records: list[dict[str, object]] = []
    rate_limit_detected = False
    rate_limit_failures = 0
    for index, symbol in enumerate(requested_symbols):
        try:
            symbol_records = adapter.fetch_symbol_records(symbol, max_observations=max_observations)
        except VendorRateLimitedError as exc:
            rate_limit_detected = True
            rate_limit_failures += 1
            invalid_records.append({"symbol": symbol, "error": _sanitize_vendor_error(str(exc))})
            latest_observation_dates[symbol] = None
            if stop_on_rate_limit or rate_limit_failures >= max_rate_limit_failures:
                break
            continue
        except Exception as exc:
            invalid_records.append({"symbol": symbol, "error": _sanitize_vendor_error(str(exc))})
            latest_observation_dates[symbol] = None
            continue
        normalized_records.extend(symbol_records)
        latest_observation_dates[symbol] = symbol_records[-1].observation_date.isoformat() if symbol_records and symbol_records[-1].observation_date else None
        if sleep_seconds_between_symbols > 0 and index < len(requested_symbols) - 1:
            time.sleep(sleep_seconds_between_symbols)
    normalized_records = tuple(
        sorted(normalized_records, key=lambda record: (record.symbol or "", record.observation_date or date.min))
    )
    return normalized_records, latest_observation_dates, rate_limit_detected, invalid_records


def _emit(
    *,
    summary: VolatilityDryRunResult,
    normalized_count: int,
    valid_count: int,
    invalid_count: int,
    show_symbols: bool,
    show_values: bool,
    show_invalid: bool,
    requested_symbols: list[str],
    rate_limit_detected: bool,
    no_vendor_calls: bool,
) -> None:
    print(f"requested_symbols={requested_symbols}")
    print(f"normalized_count={normalized_count}")
    print(f"valid_count={valid_count}")
    print(f"invalid_count={invalid_count}")
    print(f"latest_observation_dates={summary.latest_observation_dates}")
    print(f"rate_limit_detected={str(rate_limit_detected).lower()}")
    print(f"starter_symbols={list(STARTER_VOLATILITY_INDEX_SYMBOLS)}")
    print(f"no_vendor_calls={str(no_vendor_calls).lower()}")
    print(f"no_db_writes={str(summary.no_db_writes).lower()}")
    if show_symbols:
        print(f"symbols={[record.symbol for record in summary.normalized_records]}")
    if show_values:
        print(f"values={[record.value for record in summary.normalized_records]}")
    if show_invalid:
        print(f"invalid_records={summary.invalid_records}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run the volatility index foundation without database writes.")
    parser.add_argument("--live-check", action="store_true", help="Fetch live Polygon volatility observations when POLYGON_API_KEY is present.")
    parser.add_argument("--symbol", action="append", help="Specific starter symbol to fetch; defaults to all starter symbols.")
    parser.add_argument("--max-observations", type=int, default=None, help="Limit observations per symbol and keep the newest rows.")
    parser.add_argument("--show-values", action="store_true", help="Show normalized record values.")
    parser.add_argument("--sleep-seconds-between-symbols", type=float, default=0.0, help="Sleep between live symbol requests.")
    parser.add_argument("--stop-on-rate-limit", dest="stop_on_rate_limit", action="store_true", default=True)
    parser.add_argument("--no-stop-on-rate-limit", dest="stop_on_rate_limit", action="store_false")
    parser.add_argument("--max-rate-limit-failures", type=int, default=1, help="Maximum rate-limit failures tolerated before stopping.")
    parser.add_argument("--show-symbols", action="store_true", help="Show starter symbols.")
    parser.add_argument("--show-invalid", action="store_true", help="Show invalid records.")
    args = parser.parse_args(argv)

    requested_symbols = [symbol.upper() for symbol in args.symbol] if args.symbol else list(STARTER_VOLATILITY_INDEX_SYMBOLS)
    for symbol in requested_symbols:
        if symbol not in STARTER_VOLATILITY_INDEX_SYMBOLS:
            raise RuntimeError(f"unsupported starter symbol: {symbol}")

    if args.live_check:
        api_key = os.getenv("POLYGON_API_KEY")
        if not api_key:
            raise RuntimeError("POLYGON_API_KEY is required when --live-check is used")
        adapter = PolygonVolatilityIndexAdapter(PolygonVolatilityIndexSourceConfig(api_key=api_key))
        normalized_records, latest_observation_dates, rate_limit_detected, invalid_records = _normalize_live_records(
            adapter=adapter,
            requested_symbols=requested_symbols,
            max_observations=args.max_observations,
            stop_on_rate_limit=args.stop_on_rate_limit,
            max_rate_limit_failures=args.max_rate_limit_failures,
            sleep_seconds_between_symbols=args.sleep_seconds_between_symbols,
        )
        summary = VolatilityDryRunResult(
            requested_symbols=requested_symbols,
            normalized_records=normalized_records,
            invalid_records=tuple(invalid_records),
            latest_observation_dates=latest_observation_dates,
            rate_limit_detected=rate_limit_detected,
            no_vendor_calls=False,
            no_db_writes=True,
        )
        _emit(
            summary=summary,
            normalized_count=len(normalized_records),
            valid_count=len(normalized_records),
            invalid_count=len(invalid_records),
            show_symbols=args.show_symbols,
            show_values=args.show_values,
            show_invalid=args.show_invalid,
            requested_symbols=requested_symbols,
            rate_limit_detected=rate_limit_detected,
            no_vendor_calls=False,
        )
    else:
        summary = _build_summary(DEFAULT_SAMPLE_RECORDS)
        _emit(
            summary=summary,
            normalized_count=len(summary.normalized_records),
            valid_count=len(summary.normalized_records),
            invalid_count=len(summary.invalid_records),
            show_symbols=args.show_symbols,
            show_values=args.show_values,
            show_invalid=args.show_invalid,
            requested_symbols=requested_symbols,
            rate_limit_detected=False,
            no_vendor_calls=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
