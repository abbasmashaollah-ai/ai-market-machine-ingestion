from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from typing import Callable, Sequence

from app.ingestion.volatility.observations_producer import (
    VolatilityObservationProducerResult,
    build_volatility_observations_dry_run,
)
from app.vendors.common.errors import VendorRateLimitedError
from app.vendors.polygon_volatility_index import (
    PolygonVolatilityIndexAdapter,
    PolygonVolatilityIndexSourceConfig,
    is_entitlement_failure,
)


DEFAULT_SYMBOLS: tuple[str, ...] = ("VIX", "VVIX", "VXN", "RVX")


@dataclass(frozen=True)
class LiveSourceDryRunSummary:
    requested_symbols: tuple[str, ...]
    fetched_count: int
    accepted_count: int
    rejected_count: int
    warnings: tuple[str, ...]
    error_categories: tuple[str, ...]
    no_db_writes: bool = True
    no_scheduler_activation: bool = True
    no_persistence: bool = True


def _sanitize_error(message: str) -> str:
    sanitized = message
    for needle in ("POLYGON_API_KEY", "apiKey", "api-key"):
        sanitized = sanitized.replace(needle, "polygon api key")
    return sanitized


def _build_adapter() -> PolygonVolatilityIndexAdapter:
    api_key = os.getenv("POLYGON_API_KEY")
    if not api_key:
        raise RuntimeError("POLYGON_API_KEY is required when --confirm-live is used")
    return PolygonVolatilityIndexAdapter(PolygonVolatilityIndexSourceConfig(api_key=api_key))


def _print_summary(summary: LiveSourceDryRunSummary) -> None:
    print(f"requested_symbols={list(summary.requested_symbols)}")
    print(f"fetched_count={summary.fetched_count}")
    print(f"accepted_count={summary.accepted_count}")
    print(f"rejected_count={summary.rejected_count}")
    print(f"warnings={list(summary.warnings)}")
    print(f"error_categories={list(summary.error_categories)}")
    print(f"no_db_writes={str(summary.no_db_writes).lower()}")
    print(f"no_scheduler_activation={str(summary.no_scheduler_activation).lower()}")
    print(f"no_persistence={str(summary.no_persistence).lower()}")


def run_live_source_dry_run(
    *,
    requested_symbols: Sequence[str] = DEFAULT_SYMBOLS,
    confirm_live: bool,
    adapter_factory: Callable[[], PolygonVolatilityIndexAdapter] = _build_adapter,
) -> LiveSourceDryRunSummary:
    normalized_symbols = tuple(symbol.upper() for symbol in requested_symbols)
    if not confirm_live:
        raise RuntimeError("Live source dry run requires --confirm-live")

    adapter = adapter_factory()
    fetched_records: list[dict[str, object]] = []
    warnings: list[str] = []
    error_categories: list[str] = []

    for symbol in normalized_symbols:
        try:
            source_records = adapter.fetch_symbol_records(symbol)
        except VendorRateLimitedError as exc:
            warnings.append(f"{symbol}: {_sanitize_error(str(exc))}")
            error_categories.append("rate_limited")
            continue
        except Exception as exc:
            message = _sanitize_error(str(exc))
            warnings.append(f"{symbol}: {message}")
            error_categories.append("entitlement_failure" if is_entitlement_failure(message) else "vendor_error")
            continue
        fetched_records.extend(source_records)

    producer_result: VolatilityObservationProducerResult = build_volatility_observations_dry_run(fetched_records)
    warnings.extend(producer_result.warnings)
    return LiveSourceDryRunSummary(
        requested_symbols=normalized_symbols,
        fetched_count=len(fetched_records),
        accepted_count=producer_result.accepted_count,
        rejected_count=producer_result.rejected_count,
        warnings=tuple(warnings),
        error_categories=tuple(dict.fromkeys(error_categories)),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manual live-source dry run for volatility observations.")
    parser.add_argument("--confirm-live", action="store_true", help="Explicitly allow live Polygon calls for this readiness check.")
    parser.add_argument("--symbol", action="append", help="Volatility symbol to check. Defaults to VIX, VVIX, VXN, RVX.")
    args = parser.parse_args(argv)

    requested_symbols = tuple(symbol.upper() for symbol in args.symbol) if args.symbol else DEFAULT_SYMBOLS
    for symbol in requested_symbols:
        if symbol not in DEFAULT_SYMBOLS:
            raise RuntimeError(f"unsupported volatility symbol: {symbol}")

    summary = run_live_source_dry_run(requested_symbols=requested_symbols, confirm_live=args.confirm_live)
    _print_summary(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
