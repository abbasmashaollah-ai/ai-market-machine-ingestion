from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.vendor_flat_files.local_ohlcv_parser import (
    EXPECTED_DATASET_VERSION,
    EXPECTED_SCHEMA_VERSION,
    LocalFlatFileParseError,
    LocalFlatFileParseResult,
)
from app.vendor_flat_files.ohlcv_handoff_builder import build_ohlcv_handoff


SECTOR_ETF_UNIVERSE = (
    "SPY",
    "XLB",
    "XLE",
    "XLF",
    "XLI",
    "XLK",
    "XLP",
    "XLRE",
    "XLU",
    "XLV",
    "XLY",
    "XLC",
)

EXPECTED_OBSERVATION_DATE = "2026-01-15"
DEFAULT_TIMEFRAME = "1d"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a pure local sector ETF OHLCV handoff dry run.")
    parser.add_argument("--observation-date", default=EXPECTED_OBSERVATION_DATE, help="Observation date in YYYY-MM-DD format.")
    parser.add_argument("--output-file", default=None, help="Optional local file path to write the safe summary JSON.")
    return parser


def _synthetic_source_file_sha256(observation_date: str) -> str:
    seed = f"synthetic-sector-etf-ohlcv|{observation_date}|{','.join(SECTOR_ETF_UNIVERSE)}"
    import hashlib

    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def _build_synthetic_parsed_result(observation_date: str) -> LocalFlatFileParseResult:
    source_file_sha256 = _synthetic_source_file_sha256(observation_date)
    manifest = {
        "vendor": "polygon",
        "asset_class": "etfs",
        "data_type": "daily_ohlcv",
        "schema_version": EXPECTED_SCHEMA_VERSION,
        "dataset_version": EXPECTED_DATASET_VERSION,
        "validation_status": "PASS",
        "certification_status": "FIXTURE_ONLY",
        "source_file_sha256": source_file_sha256,
        "lineage_id": f"synthetic-sector-etf-handoff-{observation_date}",
        "source_file_name": f"sector_etf_ohlcv_{observation_date}.csv",
        "observation_date": observation_date,
    }
    rows: list[dict[str, object]] = []
    for index, symbol in enumerate(SECTOR_ETF_UNIVERSE, start=1):
        base = 100.0 + index
        rows.append(
            {
                "symbol": symbol,
                "observation_date": observation_date,
                "open": base,
                "high": base + 1.25,
                "low": base - 1.10,
                "close": base + 0.55,
                "volume": 1_000_000 + index * 10_000,
                "vwap": base + 0.35,
                "transactions": 1_000 + index,
                "adjusted": True,
                "vendor": "polygon",
                "asset_class": "etfs",
                "schema_version": EXPECTED_SCHEMA_VERSION,
                "dataset_version": EXPECTED_DATASET_VERSION,
                "source_file_sha256": source_file_sha256,
                "lineage_id": manifest["lineage_id"],
                "manifest_path": "synthetic://sector_etf_ohlcv",
                "source_file_name": manifest["source_file_name"],
                "validation_status": "PASS",
                "certification_status": "FIXTURE_ONLY",
            }
        )
    return LocalFlatFileParseResult(
        parse_status="PASS",
        rows=tuple(rows),
        row_count=len(rows),
        symbols=tuple(SECTOR_ETF_UNIVERSE),
        warnings=(),
        errors=(),
        manifest=manifest,
        source_file_sha256=source_file_sha256,
    )


def _summary_from_handoff(*, parsed: LocalFlatFileParseResult, handoff_result) -> dict[str, object]:
    symbols_ready = [symbol for symbol in SECTOR_ETF_UNIVERSE if symbol in set(handoff_result.symbols)]
    missing_symbols = [symbol for symbol in SECTOR_ETF_UNIVERSE if symbol not in symbols_ready]
    validation_status = "PASS" if parsed.parse_status == "PASS" else "FAIL"
    certification_status = "FIXTURE_ONLY"
    production_eligible = False
    if any(error.code == "HANDOFF_BLOCKED_VALIDATION_FAILED" for error in handoff_result.errors):
        validation_status = "FAIL"
    if any(error.code == "HANDOFF_BLOCKED_CHECKSUM_MISSING" for error in handoff_result.errors):
        validation_status = "FAIL"
    return {
        "dry_run": True,
        "observation_date": parsed.manifest.get("observation_date") if parsed.manifest else None,
        "universe_count": len(SECTOR_ETF_UNIVERSE),
        "records_generated": handoff_result.record_count,
        "symbols_ready": symbols_ready,
        "symbols_missing": missing_symbols,
        "validation_status": validation_status,
        "certification_status": certification_status,
        "production_eligible": production_eligible,
        "fixture_only": True,
        "db_write_attempted": False,
        "vendor_call_attempted": False,
        "download_attempted": False,
        "scheduler_activation_attempted": False,
        "idempotency_key_prefixes": list(handoff_result.idempotency_key_prefixes),
        "handoff_status": handoff_result.handoff_status,
        "safe_summary": handoff_result.safe_summary,
        "source_schema_version": EXPECTED_SCHEMA_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main(argv=None) -> int:
    args = _build_parser().parse_args(argv)
    parsed = _build_synthetic_parsed_result(args.observation_date)
    handoff_result = build_ohlcv_handoff(parsed)
    payload = json.dumps(_summary_from_handoff(parsed=parsed, handoff_result=handoff_result), ensure_ascii=False, indent=2, sort_keys=True)
    if args.output_file:
        output_path = Path(args.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload + "\n", encoding="utf-8")
    sys.stdout.write(payload)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
