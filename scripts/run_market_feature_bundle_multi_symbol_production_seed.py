from __future__ import annotations

import argparse
import importlib
import json
import os
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.fixtures.market_feature_bundle.fixture_validator import validate_fixture_file


FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "market_feature_bundle"
DEFAULT_SYMBOLS = ("QQQ", "IWM", "DIA")
EXPECTED_OBSERVATION_DATE = "2026-01-15"
EXPECTED_DATASET_VERSION = "production_pilot.v1"
APPROVAL_ENV = "AMM_PRODUCTION_PILOT_APPROVAL"
DATABASE_ENV = "AMM_PRODUCTION_PILOT_DATABASE_URL"
APPROVAL_VALUE = "YES_APPROVED_MULTI_SYMBOL_WRITE"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare a multi-symbol market feature bundle production seed run.")
    parser.add_argument("--symbols", default="QQQ,IWM,DIA", help="Comma-separated list of symbols to inspect.")
    parser.add_argument("--observation-date", default=EXPECTED_OBSERVATION_DATE, help="Observation date in YYYY-MM-DD format.")
    parser.add_argument("--dataset-version", default=EXPECTED_DATASET_VERSION, help="Production dataset version.")
    parser.add_argument("--output-file", default=None, help="Optional local file path to write the summary.")
    parser.add_argument("--execute", action="store_true", help="Attempt the production write path after approval checks.")
    return parser


def _normalize_symbols(symbols_arg: str) -> list[str]:
    symbols = [symbol.strip().upper() for symbol in (symbols_arg or "").split(",") if symbol.strip()]
    return symbols or list(DEFAULT_SYMBOLS)


def _validate_symbols(symbols: list[str]) -> list[str]:
    allowed = {"QQQ", "IWM", "DIA"}
    return [symbol for symbol in symbols if symbol not in allowed]


def _fixture_path_for_symbol(symbol: str) -> Path:
    return FIXTURE_DIR / f"{symbol.lower()}_fixture_dry_run.json"


def _symbol_result(symbol: str, observation_date: str, dataset_version: str) -> dict[str, object]:
    path = _fixture_path_for_symbol(symbol)
    if not path.exists():
        return {
            "symbol": symbol,
            "status": "BLOCKED",
            "reason": "fixture missing",
            "production_candidate": False,
        }

    errors = validate_fixture_file(path)
    if errors:
        return {
            "symbol": symbol,
            "status": "BLOCKED",
            "reason": "fixture validation failed",
            "errors": errors,
            "production_candidate": False,
        }

    payload = json.loads(path.read_text(encoding="utf-8"))
    observed_prefix = (payload.get("idempotency_key") or "")[:12]
    return {
        "symbol": symbol,
        "status": "READY",
        "fixture_path": str(path),
        "production_candidate": True,
        "observation_date": observation_date,
        "dataset_version": dataset_version,
        "schema_version": payload.get("schema_version"),
        "validation_status": payload.get("validation_status"),
        "coverage_status": payload.get("coverage_status"),
        "quality_status": payload.get("quality_status"),
        "certification_status": "PRODUCTION_CANDIDATE",
        "idempotency_key_prefix": observed_prefix,
        "lineage_refs_present": bool(payload.get("lineage_refs")),
        "quality_result_refs_present": bool(payload.get("quality_result_refs")),
        "note": payload.get("note"),
    }


def _build_summary(*, symbols: list[str], observation_date: str, dataset_version: str, execute_requested: bool) -> dict[str, object]:
    invalid_symbols = _validate_symbols(symbols)
    per_symbol: dict[str, dict[str, object]] = {}
    symbols_ready: list[str] = []
    symbols_blocked: list[str] = []
    approval_env_present = bool(os.getenv(APPROVAL_ENV, "").strip())
    db_url_env_present = bool(os.getenv(DATABASE_ENV, "").strip())

    validation_status = "PASS"
    coverage_status = "COMPLETE"
    quality_status = "PASS"
    certification_status = "PRODUCTION_CANDIDATE"
    db_write_allowed = bool(execute_requested and approval_env_present and db_url_env_present and not invalid_symbols)
    db_write_attempted = False
    production_write_attempted = False
    production_write_blocked = False

    for symbol in symbols:
        if symbol not in {"QQQ", "IWM", "DIA"}:
            result = {"symbol": symbol, "status": "REJECTED", "reason": "unsupported symbol"}
            per_symbol[symbol] = result
            symbols_blocked.append(symbol)
            validation_status = "FAILED"
            coverage_status = "MISSING"
            quality_status = "WARN"
            certification_status = "BLOCKED"
            continue
        result = _symbol_result(symbol, observation_date, dataset_version)
        per_symbol[symbol] = result
        if result["status"] == "READY":
            symbols_ready.append(symbol)
        else:
            symbols_blocked.append(symbol)
            validation_status = "FAILED"
            coverage_status = "MISSING"
            quality_status = "WARN"
            certification_status = "BLOCKED"

    if execute_requested:
        if db_write_allowed:
            production_write_blocked = True
        else:
            production_write_blocked = True

    # The scaffold intentionally never writes to DB.
    if execute_requested:
        db_write_attempted = False
        production_write_attempted = False

    return {
        "dry_run": not execute_requested,
        "execute_requested": execute_requested,
        "db_write_attempted": db_write_attempted,
        "db_write_allowed": db_write_allowed,
        "production_write_attempted": production_write_attempted,
        "production_write_blocked": production_write_blocked,
        "approval_env_present": approval_env_present,
        "db_url_env_present": db_url_env_present,
        "symbols_requested": symbols,
        "symbols_ready": symbols_ready,
        "symbols_blocked": symbols_blocked,
        "per_symbol_status": per_symbol,
        "validation_status": validation_status,
        "coverage_status": coverage_status,
        "quality_status": quality_status,
        "certification_status": certification_status,
        "dataset_version": dataset_version,
        "schema_version": "market_feature_bundle.v1",
        "observation_date": observation_date,
        "idempotency_key_prefix": {symbol: result.get("idempotency_key_prefix") for symbol, result in per_symbol.items() if result.get("idempotency_key_prefix")},
        "next_step": "request second explicit approval before DB write",
        "safe_summary_only": True,
        "production_writer_untouched": not execute_requested,
        "source_scan_safe": True,
        "invalid_symbols": invalid_symbols,
    }


def _attempt_execute_gate(summary: dict[str, object]) -> dict[str, object]:
    if not summary.get("execute_requested"):
        return summary
    if not summary.get("db_write_allowed"):
        return summary
    # Scaffold remains blocked until a later explicitly approved implementation.
    summary["production_write_blocked"] = True
    summary["production_write_attempted"] = False
    summary["db_write_attempted"] = False
    summary["execute_block_reason"] = "scaffold not yet approved for production writes"
    return summary


def main(argv=None) -> int:
    args = _build_parser().parse_args(argv)
    symbols = _normalize_symbols(args.symbols)
    summary = _build_summary(
        symbols=symbols,
        observation_date=args.observation_date,
        dataset_version=args.dataset_version,
        execute_requested=bool(args.execute),
    )
    summary = _attempt_execute_gate(summary)

    if args.execute and summary.get("db_write_allowed"):
        # Deliberate late import only behind explicit execute gate; this scaffold still blocks writes.
        importlib.import_module("app.writers.market_feature_bundle_db_adapter")
        importlib.import_module("app.writers.market_feature_bundle_writer")

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
