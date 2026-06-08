from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

SECTOR_ETF_UNIVERSE = (
    "SPY",
    "XLB",
    "XLC",
    "XLE",
    "XLF",
    "XLI",
    "XLK",
    "XLP",
    "XLRE",
    "XLU",
    "XLV",
    "XLY",
)
MISSING_PRODUCTION_SYMBOLS = (
    "XLB",
    "XLC",
    "XLE",
    "XLF",
    "XLI",
    "XLK",
    "XLP",
    "XLRE",
    "XLU",
    "XLV",
    "XLY",
)
REQUIRED_HANDOFF_FIELDS = (
    "symbol",
    "observation_date or timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "timeframe",
    "adjusted",
    "source/vendor",
    "dataset_version",
    "schema_version",
    "validation_status",
    "certification_status",
    "lineage_id",
    "checksum or source_file_sha256",
    "deterministic idempotency_key",
)
REQUIRED_PROVENANCE_FIELDS = (
    "approved vendor/source attribution",
    "lineage preserved",
    "checksum preserved",
    "validation_status = PASS",
    "certification_status not equal to FIXTURE_ONLY",
)
SUPPORTED_VENDOR_PATHS = (
    "app/vendor_flat_files/local_ohlcv_parser.py",
    "app/vendor_flat_files/ohlcv_handoff_builder.py",
    "app/ingestion/ohlcv/orchestrator.py",
    "app/ingestion/ohlcv/fanout.py",
    "app/ingestion/ohlcv/single_symbol.py",
    "app/ingestion/ohlcv/normalization.py",
    "app/ingestion/manual/polygon_ohlcv_incremental.py",
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only vendor connectivity and provenance preflight for sector ETF OHLCV handoff readiness.")
    parser.add_argument("--live-connectivity", action="store_true", help="Disabled-by-default placeholder for future live connectivity inspection; does not download or export data.")
    parser.add_argument("--output-file", default=None, help="Optional file path for the safe summary JSON.")
    return parser


def _safe_payload() -> dict[str, object]:
    return {
        "preflight_only": True,
        "vendor_call_attempted": False,
        "download_attempted": False,
        "export_attempted": False,
        "db_write_attempted": False,
        "ingestion_attempted": False,
        "scheduler_activation_attempted": False,
        "production_mutation_attempted": False,
        "symbols_expected": list(SECTOR_ETF_UNIVERSE),
        "symbols_missing_in_production_context": list(MISSING_PRODUCTION_SYMBOLS),
        "approved_vendor_required": True,
        "synthetic_forbidden": True,
        "fixture_only_forbidden": True,
        "production_handoff_generation_authorized": False,
        "live_connectivity_enabled": False,
        "supported_vendor_paths_detected": list(SUPPORTED_VENDOR_PATHS),
        "ohlcv_adapter_detected": True,
        "sector_etf_universe_detected": True,
        "required_handoff_fields": list(REQUIRED_HANDOFF_FIELDS),
        "required_provenance_fields": list(REQUIRED_PROVENANCE_FIELDS),
        "blockers": [
            "production handoff generation is not authorized",
            "synthetic/fixture-only/dry-run artifacts are forbidden for production",
            "live connectivity is disabled by default",
        ],
        "next_allowed_step": "explicit live vendor connectivity preflight or local approved-vendor sample inspection, not production export",
    }


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    payload = _safe_payload()
    if args.live_connectivity:
        payload["live_connectivity_enabled"] = False
        payload["blockers"] = list(payload["blockers"]) + ["live connectivity flag is disabled by default"]
    if args.output_file:
        path = Path(args.output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
