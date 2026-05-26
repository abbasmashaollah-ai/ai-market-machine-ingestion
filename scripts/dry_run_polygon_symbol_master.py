from __future__ import annotations

import argparse
import os

from app.normalization.symbol_master import validate_symbol_record
from app.vendors.polygon_symbol_master import PolygonSymbolMasterAdapter, PolygonSymbolMasterSourceConfig


def _emit(summary: dict[str, object]) -> None:
    for key in ("input_count", "normalized_count", "valid_count", "invalid_count", "vendor", "dry_run"):
        print(f"{key}={summary.get(key)}")


def _build_records(*, live_check: bool) -> list[object]:
    adapter = PolygonSymbolMasterAdapter(
        PolygonSymbolMasterSourceConfig(api_key=os.getenv("POLYGON_API_KEY") if live_check else None)
    )
    payloads = adapter.fetch_reference_tickers_raw() if live_check else adapter.build_sample_reference_payloads()
    return [adapter.map_reference_ticker(payload) for payload in payloads]


def build_summary(*, live_check: bool) -> dict[str, object]:
    records = _build_records(live_check=live_check)
    valid_records = [record for record in records if not validate_symbol_record(record)]
    return {
        "vendor": "polygon",
        "dry_run": True,
        "input_count": len(records),
        "normalized_count": len(records),
        "valid_count": len(valid_records),
        "invalid_count": len(records) - len(valid_records),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run Polygon symbol master ingestion without writing to the database.")
    parser.add_argument("--live-check", action="store_true", help="Fetch Polygon tickers when POLYGON_API_KEY is present.")
    args = parser.parse_args(argv)
    if args.live_check and not os.getenv("POLYGON_API_KEY"):
        raise RuntimeError("POLYGON_API_KEY is required for --live-check")
    summary = build_summary(live_check=args.live_check)
    _emit(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
