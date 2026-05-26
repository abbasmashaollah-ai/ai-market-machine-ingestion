from __future__ import annotations

import argparse
from datetime import datetime, timezone

from app.normalization.symbol_master import SymbolMasterSourceRecord, normalize_symbol_record, validate_source_record, validate_symbol_record


DEFAULT_SAMPLE_SOURCE = (
    SymbolMasterSourceRecord(
        symbol="AAPL",
        active=True,
        vendor="fmp",
        vendor_symbol="AAPL",
        asset_type="equity",
        exchange="NASDAQ",
        name="Apple Inc.",
        currency="USD",
        first_seen_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        last_seen_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
    ),
    SymbolMasterSourceRecord(
        symbol="SPY",
        active=True,
        vendor="polygon",
        vendor_symbol="SPY",
        asset_type="etf",
        exchange="NYSEARCA",
        name="SPDR S&P 500 ETF Trust",
        currency="USD",
        first_seen_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        last_seen_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
    ),
    SymbolMasterSourceRecord(
        symbol="VIX",
        active=False,
        vendor="polygon",
        vendor_symbol="I:VIX",
        asset_type="index",
        exchange="CBOE",
        name="CBOE Volatility Index",
        currency="USD",
        first_seen_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        last_seen_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
    ),
)


def _emit(summary: dict[str, object]) -> None:
    for key in ("input_count", "normalized_count", "valid_count", "invalid_count", "dry_run", "vendor_source"):
        print(f"{key}={summary.get(key)}")


def build_dry_run_summary(source_records: tuple[SymbolMasterSourceRecord, ...]) -> dict[str, object]:
    normalized_records = [normalize_symbol_record(record) for record in source_records]
    source_errors = [validate_source_record(record) for record in source_records]
    valid_records = [record for record, errors in zip(normalized_records, source_errors) if not errors and not validate_symbol_record(record)]
    invalid_records = [record for record, errors in zip(normalized_records, source_errors) if errors or validate_symbol_record(record)]
    return {
        "input_count": len(source_records),
        "normalized_count": len(normalized_records),
        "valid_count": len(valid_records),
        "invalid_count": len(invalid_records),
        "dry_run": True,
        "vendor_source": "sample_fixture",
        "normalized_records": tuple(normalized_records),
        "source_errors": tuple(tuple(errors) for errors in source_errors),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run symbol master ingestion without writing to the database.")
    parser.add_argument("--fixture", default="default", help="Use the built-in deterministic sample fixture.")
    args = parser.parse_args(argv)
    if args.fixture != "default":
        raise RuntimeError("only the default deterministic fixture is supported")
    summary = build_dry_run_summary(DEFAULT_SAMPLE_SOURCE)
    _emit(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
