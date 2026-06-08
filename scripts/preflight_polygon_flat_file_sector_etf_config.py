from __future__ import annotations

import argparse
import json
import os
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
REQUIRED_CONFIG_NAMES = (
    "POLYGON_API_KEY",
    "POLYGON_FLAT_FILE_ACCESS_KEY_ID",
    "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY",
    "POLYGON_FLAT_FILE_ENDPOINT",
    "POLYGON_FLAT_FILE_BUCKET",
    "POLYGON_FLAT_FILE_PREFIX",
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only Polygon flat-file sector ETF configuration preflight.")
    parser.add_argument("--output-file", default=None, help="Optional file path for the safe JSON output.")
    return parser


def _module_detected(module_path: str) -> bool:
    return (REPO_ROOT / module_path).exists()


def _safe_payload() -> dict[str, object]:
    env = os.environ
    present = [name for name in REQUIRED_CONFIG_NAMES if env.get(name)]
    missing = [name for name in REQUIRED_CONFIG_NAMES if not env.get(name)]
    parser_detected = _module_detected("app/vendor_flat_files/local_ohlcv_parser.py")
    handoff_detected = _module_detected("app/vendor_flat_files/ohlcv_handoff_builder.py")
    flat_file_adapter_detected = any(
        env.get(name)
        for name in (
            "POLYGON_FLAT_FILE_ACCESS_KEY_ID",
            "POLYGON_FLAT_FILE_SECRET_ACCESS_KEY",
            "POLYGON_FLAT_FILE_ENDPOINT",
            "POLYGON_FLAT_FILE_BUCKET",
            "POLYGON_FLAT_FILE_PREFIX",
        )
    )
    return {
        "preflight_only": True,
        "polygon_flat_file_source_selected": True,
        "vendor_call_attempted": False,
        "remote_bucket_list_attempted": False,
        "download_attempted": False,
        "export_attempted": False,
        "db_write_attempted": False,
        "ingestion_attempted": False,
        "scheduler_activation_attempted": False,
        "production_mutation_attempted": False,
        "credentials_present": bool(present),
        "credentials_printed": False,
        "required_config_names": list(REQUIRED_CONFIG_NAMES),
        "missing_config_names": missing,
        "flat_file_adapter_detected": flat_file_adapter_detected,
        "local_parser_detected": parser_detected,
        "handoff_builder_detected": handoff_detected,
        "sector_etf_universe_detected": True,
        "required_sector_symbols": list(SECTOR_ETF_UNIVERSE[1:]),
        "benchmark_symbol": "SPY",
        "production_eligible_generation_authorized": False,
        "synthetic_forbidden": True,
        "fixture_only_forbidden": True,
        "blockers": [
            "production handoff generation is not authorized",
            "no remote bucket listing or downloads are permitted in this preflight",
        ],
        "next_allowed_step": "read-only approved-vendor flat-file sample inspection or explicit production approval workflow, not export",
    }


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    payload = _safe_payload()
    safe_json = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output_file:
        path = Path(args.output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(safe_json + "\n", encoding="utf-8")
    sys.stdout.write(safe_json)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
