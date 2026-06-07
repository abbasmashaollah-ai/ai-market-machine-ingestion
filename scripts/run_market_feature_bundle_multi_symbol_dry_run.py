from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.fixtures.market_feature_bundle.fixture_validator import validate_fixture_file


FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "market_feature_bundle"
DEFAULT_SYMBOLS = ("QQQ", "IWM", "DIA")
EXPECTED_OBSERVATION_DATE = "2026-01-15"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the multi-symbol market feature bundle dry run from local fixtures.")
    parser.add_argument("--symbols", default="QQQ,IWM,DIA", help="Comma-separated list of symbols to inspect.")
    parser.add_argument("--observation-date", default=EXPECTED_OBSERVATION_DATE, help="Observation date in YYYY-MM-DD format.")
    parser.add_argument("--output-file", default=None, help="Optional local file path to write the dry-run summary.")
    return parser


def _normalize_symbols(symbols_arg: str) -> list[str]:
    if not isinstance(symbols_arg, str) or not symbols_arg.strip():
        return list(DEFAULT_SYMBOLS)
    return [symbol.strip().upper() for symbol in symbols_arg.split(",") if symbol.strip()]


def _fixture_path_for_symbol(symbol: str) -> Path:
    return FIXTURE_DIR / f"{symbol.lower()}_fixture_dry_run.json"


def _symbol_summary(symbol: str, observation_date: str) -> dict[str, object]:
    path = _fixture_path_for_symbol(symbol)
    if not path.exists():
        return {
            "symbol": symbol,
            "status": "INSUFFICIENT_EVIDENCE",
            "reason": "fixture missing",
            "fixture_path": str(path),
        }

    errors = validate_fixture_file(path)
    if errors:
        return {
            "symbol": symbol,
            "status": "FAILED",
            "reason": "fixture validation failed",
            "errors": errors,
            "fixture_path": str(path),
        }

    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        "symbol": symbol,
        "status": "PASS",
        "fixture_path": str(path),
        "observation_date": payload.get("observation_date"),
        "dataset_version": payload.get("dataset_version"),
        "schema_version": payload.get("schema_version"),
        "validation_status": payload.get("validation_status"),
        "coverage_status": payload.get("coverage_status"),
        "quality_status": payload.get("quality_status"),
        "certification_status": payload.get("certification_status"),
        "idempotency_key_prefix": (payload.get("idempotency_key") or "")[:12],
        "lineage_refs_present": bool(payload.get("lineage_refs")),
        "quality_result_refs_present": bool(payload.get("quality_result_refs")),
        "note": payload.get("note"),
    }


def _build_summary(*, symbols: list[str], observation_date: str) -> dict[str, object]:
    per_symbol: dict[str, dict[str, object]] = {}
    succeeded: list[str] = []
    failed: list[str] = []
    validation_status = "PASS"
    coverage_status = "COMPLETE"
    quality_status = "PASS"
    certification_status = "CERTIFIED"
    dataset_version = "production_pilot.fixture_dry_run.v1"
    schema_version = "market_feature_bundle.v1"
    idempotency_key_prefixes: dict[str, str] = {}

    for symbol in symbols:
        result = _symbol_summary(symbol, observation_date)
        per_symbol[symbol] = result
        if result["status"] == "PASS":
            succeeded.append(symbol)
            idempotency_key_prefixes[symbol] = str(result.get("idempotency_key_prefix", ""))
            if result.get("validation_status") != "PASS":
                validation_status = "FAILED"
            if result.get("coverage_status") != "COMPLETE":
                coverage_status = "MISSING"
            if result.get("quality_status") != "PASS":
                quality_status = "WARN"
            if result.get("certification_status") not in {"FIXTURE_CERTIFIED", "DRY_RUN_CERTIFIED"}:
                certification_status = "UNCERTIFIED"
        else:
            failed.append(symbol)
            if result.get("status") != "INSUFFICIENT_EVIDENCE":
                validation_status = "FAILED"
            coverage_status = "MISSING"
            quality_status = "WARN"
            certification_status = "UNCERTIFIED"

    return {
        "dry_run": True,
        "db_write_attempted": False,
        "production_write_attempted": False,
        "vendor_call_attempted": False,
        "live_api_call_attempted": False,
        "scheduler_activation_attempted": False,
        "symbols_requested": symbols,
        "symbols_succeeded": succeeded,
        "symbols_failed": failed,
        "per_symbol_status": per_symbol,
        "validation_status": validation_status,
        "coverage_status": coverage_status,
        "quality_status": quality_status,
        "certification_status": certification_status,
        "dataset_version": dataset_version,
        "schema_version": schema_version,
        "observation_date": observation_date,
        "idempotency_key_prefix": idempotency_key_prefixes,
        "fixture_local_mode": True,
        "production_writer_untouched": True,
        "source_scan_safe": True,
    }


def main(argv=None) -> int:
    args = _build_parser().parse_args(argv)
    symbols = _normalize_symbols(args.symbols)
    summary = _build_summary(symbols=symbols, observation_date=args.observation_date)
    payload = json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output_file:
        output_path = Path(args.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload + "\n", encoding="utf-8")
    sys.stdout.write(payload)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
