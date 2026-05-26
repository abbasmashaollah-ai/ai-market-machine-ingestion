from __future__ import annotations

import argparse
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Iterable

from scripts.manual_ohlcv_preflight import build_preflight_report as build_fmp_preflight_report
from scripts.preflight_polygon_ohlcv_operations import build_preflight_report as build_polygon_preflight_report
from scripts.verify_manual_ingestion_commands import MODULES as MANUAL_COMMAND_MODULES


REQUIRED_MANUAL_COMMANDS = (
    "scripts.assess_ohlcv_scheduler_readiness",
    "scripts.run_fmp_ohlcv_daily_update",
    "scripts.preflight_fmp_ohlcv_operations",
    "scripts.verify_fmp_ohlcv_evidence_chain",
    "scripts.run_polygon_ohlcv_chunked_backfill",
    "scripts.preflight_polygon_ohlcv_operations",
    "scripts.verify_polygon_ohlcv_evidence_chain",
)

REQUIRED_DOCS = (
    Path("docs/manual_ohlcv_preflight.md"),
    Path("docs/manual_ingestion_command_verification.md"),
    Path("docs/ohlcv_scheduler_readiness.md"),
)

OPTIONAL_DOCS = (
    Path("docs/fmp_daily_ohlcv_manual_runner.md"),
    Path("docs/fmp_ohlcv_evidence_chain_verification.md"),
    Path("docs/polygon_ohlcv_gap_fill.md"),
    Path("docs/polygon_ohlcv_evidence_chain_verification.md"),
)

REQUIRED_TESTS = (
    Path("tests/unit/test_preflight_fmp_ohlcv_operations.py"),
    Path("tests/unit/test_preflight_polygon_ohlcv_operations.py"),
    Path("tests/unit/test_verify_fmp_ohlcv_evidence_chain.py"),
    Path("tests/unit/test_verify_polygon_ohlcv_evidence_chain.py"),
    Path("tests/unit/test_verify_manual_ingestion_commands.py"),
)

OPTIONAL_TESTS = (
    Path("tests/unit/test_writer_contracts.py"),
    Path("tests/unit/test_boundary_guardrails.py"),
    Path("tests/unit/test_evidence_chain_helpers.py"),
)

ACTIVE_SCHEDULER_FILES = (
    Path("scripts/start_scheduler.py"),
    Path("app/scheduler/scheduler.py"),
)

RAILWAY_CONFIG = Path("railway.json")
RAILWAY_START = Path("scripts/railway_start.py")

def _marker(*parts: str) -> str:
    return "".join(parts)


FORBIDDEN_IMPORT_MARKERS = (
    _marker("Fast", "API"),
    _marker("API", "Router"),
    _marker("ale", "mbic"),
    _marker("from ai_market_machine_", "data"),
    _marker("import ai_market_machine_", "data"),
)

MANUAL_COMMAND_SOURCE_PATHS = (
    Path("scripts/assess_ohlcv_scheduler_readiness.py"),
    Path("scripts/manual_ohlcv_preflight.py"),
    Path("scripts/preflight_fmp_ohlcv_operations.py"),
    Path("scripts/preflight_polygon_ohlcv_operations.py"),
    Path("scripts/run_fmp_ohlcv_daily_update.py"),
    Path("scripts/run_polygon_ohlcv_chunked_backfill.py"),
    Path("scripts/verify_fmp_ohlcv_evidence_chain.py"),
    Path("scripts/verify_polygon_ohlcv_evidence_chain.py"),
    Path("scripts/verify_manual_ingestion_commands.py"),
)


def _exists(path: Path) -> bool:
    return path.exists()


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _scan_for_markers(path: Path, markers: Iterable[str]) -> list[str]:
    if not _exists(path):
        return [f"{path}:missing"]
    text = _read_text(path)
    return [f"{path}:{marker}" for marker in markers if marker in text]


def _inventory_complete() -> bool:
    missing = [module for module in REQUIRED_MANUAL_COMMANDS if module not in MANUAL_COMMAND_MODULES]
    return not missing


def _manual_command_imports_are_safe() -> list[str]:
    violations: list[str] = []
    for path in MANUAL_COMMAND_SOURCE_PATHS:
        if path == Path("scripts/assess_ohlcv_scheduler_readiness.py"):
            continue
        violations.extend(_scan_for_markers(path, FORBIDDEN_IMPORT_MARKERS))
    return violations


def _run_preflight(builder: object, args: argparse.Namespace) -> tuple[str, str, dict[str, object]]:
    try:
        _, summary = builder(args)
    except Exception as exc:  # pragma: no cover - exercised by tests
        return "FAIL", str(exc), {}
    detail = str(summary.get("preflight_status", "unknown"))
    return "PASS", detail, dict(summary)


def _build_fmp_args() -> argparse.Namespace:
    return SimpleNamespace(
        vendor="fmp",
        symbol=None,
        as_of_date="2026-01-14",
        timeframe="1d",
        max_symbols=3,
        max_requests=10,
        check_existing=False,
        confirm_write=False,
        record_run=False,
        record_quality=False,
        record_lineage=False,
    )


def _build_polygon_args() -> argparse.Namespace:
    return SimpleNamespace(
        symbol=None,
        as_of_date="2026-01-14",
        timeframe="1d",
        source="polygon_aggregates",
        max_symbols=25,
        max_requests=10,
        check_existing=False,
    )


def _status_from_optional_exist(*paths: Path) -> tuple[str, list[str]]:
    missing = [str(path) for path in paths if not _exists(path)]
    return ("PASS" if not missing else "WARN", missing)


def build_scheduler_readiness_report() -> dict[str, object]:
    manual_inventory_status = "PASS" if _inventory_complete() else "FAIL"
    manual_import_violations = _manual_command_imports_are_safe()
    manual_import_status = "PASS" if not manual_import_violations else "FAIL"

    fmp_preflight_status, fmp_preflight_detail, fmp_preflight_summary = _run_preflight(
        build_fmp_preflight_report, _build_fmp_args()
    )
    polygon_preflight_status, polygon_preflight_detail, polygon_preflight_summary = _run_preflight(
        build_polygon_preflight_report, _build_polygon_args()
    )

    docs_status, missing_docs = _status_from_optional_exist(*REQUIRED_DOCS)
    optional_docs_status, missing_optional_docs = _status_from_optional_exist(*OPTIONAL_DOCS)
    tests_status, missing_tests = _status_from_optional_exist(*REQUIRED_TESTS)
    optional_tests_status, missing_optional_tests = _status_from_optional_exist(*OPTIONAL_TESTS)

    evidence_tools_status = "PASS" if all(
        _exists(path)
        for path in (
            Path("scripts/verify_fmp_ohlcv_evidence_chain.py"),
            Path("scripts/verify_polygon_ohlcv_evidence_chain.py"),
        )
    ) else "WARN"

    scheduler_activation_blockers = [str(path) for path in ACTIVE_SCHEDULER_FILES if _exists(path)]
    railway_config_status = "PASS"
    railway_blockers: list[str] = []
    if not _exists(RAILWAY_CONFIG) or not _exists(RAILWAY_START):
        railway_config_status = "FAIL"
        railway_blockers.extend([str(path) for path in (RAILWAY_CONFIG, RAILWAY_START) if not _exists(path)])
    else:
        railway_text = _read_text(RAILWAY_CONFIG).lower()
        if "scheduler" in railway_text or "start_scheduler" in railway_text:
            railway_config_status = "FAIL"
            railway_blockers.append("railway.json references scheduler activation")

    scheduler_activation_status = "FAIL" if scheduler_activation_blockers or railway_config_status == "FAIL" else "PASS"

    blockers: list[str] = []
    if manual_inventory_status == "FAIL":
        blockers.append("manual_command_inventory_incomplete")
    if manual_import_status == "FAIL":
        blockers.append("forbidden_imports_in_manual_commands")
    if fmp_preflight_status == "FAIL":
        blockers.append("fmp_preflight_failed")
    if polygon_preflight_status == "FAIL":
        blockers.append("polygon_preflight_failed")
    if scheduler_activation_status == "FAIL":
        blockers.append("scheduler_activation_files_exist_too_early")
        blockers.extend(f"railway:{item}" for item in railway_blockers)

    warnings: list[str] = []
    if docs_status == "WARN":
        warnings.extend(f"missing_required_doc:{item}" for item in missing_docs)
    if optional_docs_status == "WARN":
        warnings.extend(f"missing_optional_doc:{item}" for item in missing_optional_docs)
    if tests_status == "WARN":
        warnings.extend(f"missing_required_test:{item}" for item in missing_tests)
    if optional_tests_status == "WARN":
        warnings.extend(f"missing_optional_test:{item}" for item in missing_optional_tests)
    if evidence_tools_status == "WARN":
        warnings.append("evidence_verifiers_missing")

    if blockers:
        scheduler_readiness_status = "FAIL"
    elif warnings:
        scheduler_readiness_status = "WARN"
    else:
        scheduler_readiness_status = "PASS"

    score = 100
    score -= 25 if manual_inventory_status == "FAIL" else 0
    score -= 20 if manual_import_status == "FAIL" else 0
    score -= 20 if fmp_preflight_status == "FAIL" else 0
    score -= 20 if polygon_preflight_status == "FAIL" else 0
    score -= 10 if scheduler_activation_status == "FAIL" else 0
    score -= 5 * len(warnings)
    score = max(0, min(100, score))

    manual_foundations = {
        "manual_inventory_status": manual_inventory_status,
        "manual_import_status": manual_import_status,
        "fmp_preflight_status": fmp_preflight_status,
        "fmp_preflight_detail": fmp_preflight_detail,
        "polygon_preflight_status": polygon_preflight_status,
        "polygon_preflight_detail": polygon_preflight_detail,
        "evidence_tools_status": evidence_tools_status,
        "docs_status": docs_status,
        "tests_status": tests_status,
        "scheduler_activation_status": scheduler_activation_status,
        "railway_status": railway_config_status,
        "fmp_preflight_summary": fmp_preflight_summary,
        "polygon_preflight_summary": polygon_preflight_summary,
    }

    return {
        "scheduler_readiness_status": scheduler_readiness_status,
        "readiness_score": score,
        "checklist": manual_foundations,
        "blockers": tuple(blockers),
        "warnings": tuple(warnings),
        "next_required_step": "address_blockers" if blockers else "fill_optional_readiness_gaps" if warnings else "none",
    }


def main() -> int:
    report = build_scheduler_readiness_report()
    print(f"scheduler_readiness_status={report['scheduler_readiness_status']}")
    print(f"readiness_score={report['readiness_score']}")
    for key, value in report["checklist"].items():
        if isinstance(value, dict):
            print(f"{key}={json.dumps(value, sort_keys=True)}")
        else:
            print(f"{key}={value}")
    print(f"blockers={','.join(report['blockers']) if report['blockers'] else 'none'}")
    print(f"warnings={','.join(report['warnings']) if report['warnings'] else 'none'}")
    print(f"next_required_step={report['next_required_step']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
