from __future__ import annotations

import argparse
from datetime import date

from app.normalization.volatility_index import (
    NormalizedVolatilityIndexRecord,
    STARTER_VOLATILITY_INDEX_SYMBOLS,
    normalize_volatility_index_record,
    validate_volatility_index_record,
)


DEFAULT_SAMPLE_RECORDS: tuple[dict[str, object], ...] = (
    {"symbol": "VIX", "observation_date": "2026-05-21", "value": 18.2, "source": "sample_fixture", "vendor_symbol": "VIX", "unit": "index", "notes": "deterministic fixture"},
    {"symbol": "VVIX", "observation_date": "2026-05-21", "value": 92.1, "source": "sample_fixture", "vendor_symbol": "VVIX", "unit": "index", "notes": "deterministic fixture"},
    {"symbol": "VXN", "observation_date": "2026-05-21", "value": 21.7, "source": "sample_fixture", "vendor_symbol": "VXN", "unit": "index", "notes": "deterministic fixture"},
    {"symbol": "RVX", "observation_date": "2026-05-21", "value": 25.4, "source": "sample_fixture", "vendor_symbol": "RVX", "unit": "index", "notes": "deterministic fixture"},
)


def _build_summary(source_records: tuple[dict[str, object], ...]) -> dict[str, object]:
    normalized_records = tuple(normalize_volatility_index_record(record) for record in source_records)
    valid_records = tuple(record for record in normalized_records if not validate_volatility_index_record(record))
    invalid_records = tuple(record for record in normalized_records if validate_volatility_index_record(record))
    return {
        "symbol_count": len({record.get("symbol") for record in source_records}),
        "normalized_count": len(normalized_records),
        "valid_count": len(valid_records),
        "invalid_count": len(invalid_records),
        "starter_symbols": ",".join(STARTER_VOLATILITY_INDEX_SYMBOLS),
        "no_vendor_calls": True,
        "no_db_writes": True,
        "normalized_records": normalized_records,
        "invalid_records": invalid_records,
    }


def _emit(summary: dict[str, object], *, show_symbols: bool, show_invalid: bool) -> None:
    print(f"symbol_count={summary['symbol_count']}")
    print(f"normalized_count={summary['normalized_count']}")
    print(f"valid_count={summary['valid_count']}")
    print(f"invalid_count={summary['invalid_count']}")
    print(f"starter_symbols={summary['starter_symbols']}")
    print(f"no_vendor_calls={str(summary['no_vendor_calls']).lower()}")
    print(f"no_db_writes={str(summary['no_db_writes']).lower()}")
    if show_symbols:
        print(f"symbols={[record.symbol for record in summary['normalized_records']]}")
    if show_invalid:
        print(f"invalid_records={summary['invalid_records']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run the volatility index foundation without vendor calls or database writes.")
    parser.add_argument("--show-symbols", action="store_true", help="Print the normalized starter symbols.")
    parser.add_argument("--show-invalid", action="store_true", help="Print invalid normalized records.")
    args = parser.parse_args(argv)
    summary = _build_summary(DEFAULT_SAMPLE_RECORDS)
    _emit(summary, show_symbols=args.show_symbols, show_invalid=args.show_invalid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
