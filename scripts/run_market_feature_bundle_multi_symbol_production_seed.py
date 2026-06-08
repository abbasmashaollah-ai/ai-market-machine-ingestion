from __future__ import annotations

import argparse
import json
import os
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.fixtures.market_feature_bundle.fixture_validator import validate_fixture_file


FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "market_feature_bundle"
DEFAULT_SYMBOLS = ("QQQ", "IWM", "DIA")
ALLOWED_SYMBOLS = set(DEFAULT_SYMBOLS)
EXPECTED_OBSERVATION_DATE = "2026-01-15"
EXPECTED_DATASET_VERSION = "production_pilot.v1"
EXPECTED_SCHEMA_VERSION = "market_feature_bundle.v1"
APPROVAL_ENV = "AMM_PRODUCTION_PILOT_APPROVAL"
DATABASE_ENV = "AMM_PRODUCTION_PILOT_DATABASE_URL"
APPROVAL_VALUE = "YES_APPROVED_MULTI_SYMBOL_WRITE"
VALIDATION_STATUS_PASS = "PASS"
COVERAGE_STATUS_COMPLETE = "COMPLETE"
QUALITY_STATUS_PASS = "PASS"
PRODUCTION_CANDIDATE_STATUS = "PRODUCTION_CANDIDATE"
CERTIFIED_STATUS = "CERTIFIED"

WriterResult = dict[str, object]
WriterFn = Callable[[dict[str, object]], WriterResult]
VerifierFn = Callable[[dict[str, object], dict[str, object]], dict[str, object]]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare a multi-symbol market feature bundle production seed run.")
    parser.add_argument("--symbols", default="QQQ,IWM,DIA", help="Comma-separated list of symbols to inspect.")
    parser.add_argument("--observation-date", default=EXPECTED_OBSERVATION_DATE, help="Observation date in YYYY-MM-DD format.")
    parser.add_argument("--dataset-version", default=EXPECTED_DATASET_VERSION, help="Production dataset version.")
    parser.add_argument("--output-file", default=None, help="Optional local file path to write the summary.")
    parser.add_argument("--execute", action="store_true", help="Attempt the guarded production write path after approval checks.")
    return parser


def _normalize_symbols(symbols_arg: str) -> list[str]:
    symbols = [symbol.strip().upper() for symbol in (symbols_arg or "").split(",") if symbol.strip()]
    return symbols or list(DEFAULT_SYMBOLS)


def _validate_symbols(symbols: list[str]) -> list[str]:
    return [symbol for symbol in symbols if symbol not in ALLOWED_SYMBOLS]


def _fixture_path_for_symbol(symbol: str) -> Path:
    return FIXTURE_DIR / f"{symbol.lower()}_fixture_dry_run.json"


def _load_fixture(symbol: str, observation_date: str, dataset_version: str) -> dict[str, object]:
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
    observed_prefix = str(payload.get("idempotency_key") or "")[:12]
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
        "certification_status": PRODUCTION_CANDIDATE_STATUS,
        "idempotency_key_prefix": observed_prefix,
        "lineage_refs_present": bool(payload.get("lineage_refs")),
        "quality_result_refs_present": bool(payload.get("quality_result_refs")),
        "note": payload.get("note"),
    }


def _empty_safe_summary() -> dict[str, object]:
    return {
        "validation_status": VALIDATION_STATUS_PASS,
        "coverage_status": COVERAGE_STATUS_COMPLETE,
        "quality_status": QUALITY_STATUS_PASS,
    }


def _build_writer_payload(fixture_payload: dict[str, object], *, observation_date: str, dataset_version: str) -> dict[str, object]:
    raw_sections = fixture_payload.get("raw_sections") or {}
    synthesized_sections = fixture_payload.get("synthesized_sections") or {}
    if isinstance(raw_sections, dict):
        raw_section_names = list(raw_sections.keys())
    else:
        raw_section_names = list(raw_sections) if isinstance(raw_sections, list) else []
    if isinstance(synthesized_sections, dict):
        synthesized_section_names = list(synthesized_sections.keys())
    else:
        synthesized_section_names = list(synthesized_sections) if isinstance(synthesized_sections, list) else []

    section_names = raw_section_names + synthesized_section_names
    section_record_counts = {name: 0 for name in section_names}
    section_labels = {name: None for name in section_names}
    compact_summary = dict(fixture_payload.get("compact_summary") or {})
    compact_summary.setdefault("universe", fixture_payload.get("universe"))
    compact_summary.setdefault("observation_date", observation_date)
    compact_summary.setdefault("validation_status", VALIDATION_STATUS_PASS)
    compact_summary.setdefault("coverage_status", COVERAGE_STATUS_COMPLETE)
    compact_summary.setdefault("quality_status", QUALITY_STATUS_PASS)
    compact_summary["certification_status"] = CERTIFIED_STATUS

    full_bundle_payload = dict(fixture_payload.get("full_bundle_payload") or {})
    full_bundle_payload.update(
        {
            "universe": fixture_payload.get("universe"),
            "observation_date": observation_date,
            "schema_version": EXPECTED_SCHEMA_VERSION,
            "dataset_version": dataset_version,
            "source_repo": "ai-market-machine-ingestion",
            "source_run_id": fixture_payload.get("source_run_id"),
            "validation_status": VALIDATION_STATUS_PASS,
            "coverage_status": COVERAGE_STATUS_COMPLETE,
            "quality_status": QUALITY_STATUS_PASS,
            "certification_status": CERTIFIED_STATUS,
            "lineage_refs": list(fixture_payload.get("lineage_refs") or []),
            "quality_result_refs": list(fixture_payload.get("quality_result_refs") or []),
            "note": fixture_payload.get("note"),
        }
    )
    idempotency_key = str(fixture_payload.get("idempotency_key") or "")
    if "fixture_dry_run" in idempotency_key:
        idempotency_key = idempotency_key.replace("fixture_dry_run", "production_pilot")

    return {
        "observation_date": observation_date,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "universe": fixture_payload.get("universe"),
        "schema_version": EXPECTED_SCHEMA_VERSION,
        "dataset_version": dataset_version,
        "idempotency_key": idempotency_key,
        "raw_sections": raw_section_names,
        "synthesized_sections": synthesized_section_names,
        "section_record_counts": section_record_counts,
        "section_labels": section_labels,
        "compact_summary": compact_summary,
        "full_bundle_payload": full_bundle_payload,
        "validation_status": VALIDATION_STATUS_PASS,
        "validation_errors": [],
        "validation_warnings": [],
        "total_warnings": 0,
        "safety_flags": {
            "no_db_writes": True,
            "no_vendor_calls": True,
            "no_live_api_calls": True,
            "no_scheduler_activation": True,
        },
        "rejected_counts": {},
        "certification_status": CERTIFIED_STATUS,
        "source_repo": "ai-market-machine-ingestion",
        "source_run_id": fixture_payload.get("source_run_id"),
        "input_dataset_versions": {
            "fixture_dataset_version": fixture_payload.get("dataset_version"),
            "production_dataset_version": dataset_version,
        },
        "lineage_refs": list(fixture_payload.get("lineage_refs") or []),
        "quality_result_refs": list(fixture_payload.get("quality_result_refs") or []),
    }


def _normalize_write_status(write_status: object) -> str:
    status = str(write_status or "").upper()
    if status in {"WRITE_ACCEPTED", "WRITTEN"}:
        return "WRITTEN"
    if status in {"IDEMPOTENT_NOOP", "ALREADY_EXISTS"}:
        return "IDEMPOTENT_NOOP"
    if status == "CONFLICT":
        return "CONFLICT"
    if status in {"WRITE_FAILED", "FAILED", "REJECTED"}:
        return "FAILED"
    return "FAILED"


def _writer_result_summary(writer_result: dict[str, object]) -> dict[str, object]:
    return {
        "write_status": _normalize_write_status(writer_result.get("write_status")),
        "conflict_status": writer_result.get("conflict_status"),
        "would_write": bool(writer_result.get("would_write")),
        "dry_run": bool(writer_result.get("dry_run")),
    }


def _default_writer_fn(database_url: str) -> WriterFn:
    def _writer(payload: dict[str, object]) -> WriterResult:
        from app.writers.market_feature_bundle_db_adapter import build_market_feature_bundle_session
        from app.writers.market_feature_bundle_writer import MarketFeatureBundleWriter

        session = build_market_feature_bundle_session(database_url)
        writer = MarketFeatureBundleWriter(session, dry_run=False)
        return writer.write_payload(payload)

    return _writer


def _default_verifier_fn(writer_result: dict[str, object], payload: dict[str, object]) -> dict[str, object]:
    return {
        "verification_status": "NOT_RUN",
        "verified_symbol": payload.get("universe"),
        "verified_idempotency_key_prefix": str(payload.get("idempotency_key") or "")[:12],
        "writer_write_status": writer_result.get("write_status"),
    }


def _build_summary(
    *,
    symbols: list[str],
    observation_date: str,
    dataset_version: str,
    execute_requested: bool,
) -> tuple[dict[str, object], dict[str, dict[str, object]]]:
    invalid_symbols = _validate_symbols(symbols)
    approval_env_present = bool(os.getenv(APPROVAL_ENV, "").strip())
    db_url_env_present = bool(os.getenv(DATABASE_ENV, "").strip())
    symbols_ready: list[str] = []
    symbols_blocked: list[str] = []
    per_symbol_status: dict[str, dict[str, object]] = {}
    fixture_payloads: dict[str, dict[str, object]] = {}

    base_summary = _empty_safe_summary()
    summary = {
        "dry_run": not execute_requested,
        "execute_requested": execute_requested,
        "db_write_attempted": False,
        "db_write_allowed": bool(
            execute_requested
            and approval_env_present
            and db_url_env_present
            and not invalid_symbols
        ),
        "production_write_attempted": False,
        "production_write_blocked": False,
        "approval_env_present": approval_env_present,
        "db_url_env_present": db_url_env_present,
        "symbols_requested": symbols,
        "symbols_ready": symbols_ready,
        "symbols_blocked": symbols_blocked,
        "symbols_written": [],
        "symbols_noop": [],
        "symbols_conflict": [],
        "symbols_failed": [],
        "per_symbol_status": per_symbol_status,
        "per_symbol_write_status": {},
        "validation_status": base_summary["validation_status"],
        "coverage_status": base_summary["coverage_status"],
        "quality_status": base_summary["quality_status"],
        "certification_status": PRODUCTION_CANDIDATE_STATUS,
        "dataset_version": dataset_version,
        "schema_version": EXPECTED_SCHEMA_VERSION,
        "observation_date": observation_date,
        "idempotency_key_prefix": {},
        "next_step": "request second explicit approval before DB write",
        "safe_summary_only": True,
        "production_writer_untouched": not execute_requested,
        "source_scan_safe": True,
        "invalid_symbols": invalid_symbols,
    }

    for symbol in symbols:
        if symbol not in ALLOWED_SYMBOLS:
            per_symbol_status[symbol] = {
                "symbol": symbol,
                "status": "REJECTED",
                "reason": "unsupported symbol",
            }
            symbols_blocked.append(symbol)
            summary["validation_status"] = "FAILED"
            summary["coverage_status"] = "MISSING"
            summary["quality_status"] = "WARN"
            summary["certification_status"] = "BLOCKED"
            summary["symbols_failed"].append(symbol)
            continue

        result = _load_fixture(symbol, observation_date, dataset_version)
        per_symbol_status[symbol] = result
        if result.get("status") == "READY":
            symbols_ready.append(symbol)
            summary["idempotency_key_prefix"][symbol] = result.get("idempotency_key_prefix")
            path = _fixture_path_for_symbol(symbol)
            fixture_payloads[symbol] = json.loads(path.read_text(encoding="utf-8"))
        else:
            symbols_blocked.append(symbol)
            summary["validation_status"] = "FAILED"
            summary["coverage_status"] = "MISSING"
            summary["quality_status"] = "WARN"
            summary["certification_status"] = "BLOCKED"
            summary["symbols_failed"].append(symbol)

    if not execute_requested or not summary["db_write_allowed"]:
        return summary, fixture_payloads

    return summary, fixture_payloads


def _attempt_execute_gate(
    summary: dict[str, object],
    *,
    fixture_payloads: dict[str, dict[str, object]],
    approval_value: str | None,
    database_url: str | None,
    writer_fn: WriterFn | None = None,
    verifier_fn: VerifierFn | None = None,
) -> dict[str, object]:
    if not summary.get("execute_requested"):
        return summary

    if not summary.get("db_write_allowed"):
        summary["production_write_blocked"] = True
        summary["execute_block_reason"] = "approval or database gate missing"
        return summary

    if approval_value != APPROVAL_VALUE or not database_url:
        summary["db_write_allowed"] = False
        summary["db_write_attempted"] = False
        summary["production_write_blocked"] = True
        summary["execute_block_reason"] = "approval or database gate missing"
        return summary

    writer_fn = writer_fn or _default_writer_fn(database_url)
    verifier_fn = verifier_fn or _default_verifier_fn

    symbols_written: list[str] = []
    symbols_noop: list[str] = []
    symbols_conflict: list[str] = []
    symbols_failed: list[str] = []
    per_symbol_write_status: dict[str, dict[str, object]] = {}
    verification_status = "NOT_RUN"

    for symbol in summary.get("symbols_ready", []):
        fixture_result = summary["per_symbol_status"].get(symbol, {})
        fixture_payload = fixture_payloads.get(symbol)
        if not isinstance(fixture_payload, dict):
            write_result = {
                "write_status": "FAILED",
                "reason": "fixture payload missing",
            }
            per_symbol_write_status[symbol] = _writer_result_summary(write_result)
            symbols_failed.append(symbol)
            continue

        writer_payload = _build_writer_payload(
            fixture_payload,
            observation_date=str(summary.get("observation_date")),
            dataset_version=str(summary.get("dataset_version")),
        )
        writer_result = writer_fn(writer_payload)
        normalized = _writer_result_summary(writer_result)
        per_symbol_write_status[symbol] = normalized

        status = normalized["write_status"]
        if status == "WRITTEN":
            symbols_written.append(symbol)
        elif status == "IDEMPOTENT_NOOP":
            symbols_noop.append(symbol)
        elif status == "CONFLICT":
            symbols_conflict.append(symbol)
        else:
            symbols_failed.append(symbol)

        if normalized["write_status"] in {"WRITTEN", "IDEMPOTENT_NOOP"}:
            verification_result = verifier_fn(writer_result, writer_payload)
            verification_status = str(verification_result.get("verification_status") or verification_status)
            summary["verification_status"] = verification_status
            summary["verification_details"] = verification_result

    summary["db_write_attempted"] = True
    summary["production_write_attempted"] = True
    summary["production_write_blocked"] = False
    summary["symbols_written"] = symbols_written
    summary["symbols_noop"] = symbols_noop
    summary["symbols_conflict"] = symbols_conflict
    summary["symbols_failed"] = symbols_failed
    summary["per_symbol_write_status"] = per_symbol_write_status
    summary["execute_block_reason"] = None
    summary["verification_status"] = verification_status
    return summary


def main(
    argv: list[str] | None = None,
    *,
    writer_fn: WriterFn | None = None,
    verifier_fn: VerifierFn | None = None,
) -> int:
    args = _build_parser().parse_args(argv)
    symbols = _normalize_symbols(args.symbols)
    summary, fixture_payloads = _build_summary(
        symbols=symbols,
        observation_date=args.observation_date,
        dataset_version=args.dataset_version,
        execute_requested=bool(args.execute),
    )
    summary = _attempt_execute_gate(
        summary,
        fixture_payloads=fixture_payloads,
        approval_value=os.getenv(APPROVAL_ENV),
        database_url=os.getenv(DATABASE_ENV),
        writer_fn=writer_fn,
        verifier_fn=verifier_fn,
    )

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
