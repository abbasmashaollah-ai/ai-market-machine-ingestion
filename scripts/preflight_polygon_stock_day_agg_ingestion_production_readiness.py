from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_SCRIPTS = (
    "scripts/inspect_polygon_stock_day_agg_quarantine_file.py",
    "scripts/preview_normalize_polygon_stock_day_agg_quarantine_file.py",
    "scripts/preview_polygon_stock_day_agg_warehouse_handoff_candidate.py",
    "scripts/write_polygon_stock_day_agg_local_handoff_artifact.py",
    "scripts/write_polygon_stock_day_agg_batch_local_handoff_artifacts.py",
    "scripts/validate_polygon_stock_day_agg_local_handoff_artifacts.py",
    "scripts/build_polygon_stock_day_agg_data_repo_intake_package.py",
)

REQUIRED_TESTS = (
    "tests/scripts/test_inspect_polygon_stock_day_agg_quarantine_file.py",
    "tests/scripts/test_preview_normalize_polygon_stock_day_agg_quarantine_file.py",
    "tests/scripts/test_preview_polygon_stock_day_agg_warehouse_handoff_candidate.py",
    "tests/scripts/test_write_polygon_stock_day_agg_local_handoff_artifact.py",
    "tests/scripts/test_write_polygon_stock_day_agg_batch_local_handoff_artifacts.py",
    "tests/scripts/test_validate_polygon_stock_day_agg_local_handoff_artifacts.py",
    "tests/scripts/test_build_polygon_stock_day_agg_data_repo_intake_package.py",
)

REQUIRED_DOCS = (
    "docs/polygon_stock_day_agg_quarantine_parse_inspection.md",
    "docs/polygon_stock_day_agg_local_normalization_preview.md",
    "docs/polygon_stock_day_agg_warehouse_handoff_candidate_preview.md",
    "docs/polygon_stock_day_agg_local_handoff_artifact_writer.md",
    "docs/polygon_stock_day_agg_batch_local_handoff_artifact_writer.md",
    "docs/polygon_stock_day_agg_local_handoff_artifact_validator.md",
    "docs/polygon_stock_day_agg_data_repo_intake_package.md",
)

GENERATED_PATTERNS = ("outputs/", "output/", "artifacts/", "artifact/")
PRODUCTION_DB_WRITE_SIGNATURES = (
    "database_url",
    "prod_database_url",
    "production_database_url",
    "railway production database",
    "production_db_write",
    "write_production",
    "production migration",
    "alembic upgrade head",
    "alembic upgrade",
)
SCHEDULER_ACTIVATION_SIGNATURES = (
    "--enable-scheduler-cycle",
    "enable_scheduler_cycle",
    "enable_scheduler=true",
    "scheduler_cycle_enabled = true",
    "scheduler_cycle_enabled=true",
    "run_polygon_ohlcv_scheduler_cycle",
)
DATA_REPO_MUTATION_SIGNATURES = (
    "direct mutation of ai-market-machine-data",
    "direct data repo write",
    "direct data repo mutation",
    "write to ai-market-machine-data",
    "mutate ai-market-machine-data",
)


def _exists(paths: tuple[str, ...]) -> list[str]:
    return [path for path in paths if (REPO_ROOT / path).exists()]


def _git_ls_files(*args: str) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def _git_status_short() -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "status", "--short", "-uall"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def _scan_for_blockers() -> dict[str, bool]:
    text_blobs: list[str] = []
    for rel in REQUIRED_SCRIPTS:
        path = REPO_ROOT / rel
        if path.exists():
            text_blobs.append(path.read_text(encoding="utf-8").lower())
    text = "\n".join(text_blobs)
    production_db_write_detected = any(token in text for token in PRODUCTION_DB_WRITE_SIGNATURES)
    scheduler_activation_detected = any(token in text for token in SCHEDULER_ACTIVATION_SIGNATURES)
    data_repo_mutation_detected = any(token in text for token in DATA_REPO_MUTATION_SIGNATURES)
    return {
        "production_db_write_detected": production_db_write_detected,
        "scheduler_activation_detected": scheduler_activation_detected,
        "data_repo_mutation_detected": data_repo_mutation_detected,
    }


def _generated_artifact_flags() -> tuple[bool, bool]:
    tracked = False
    untracked = False
    status_lines = _git_status_short()
    tracked_paths = set(_git_ls_files())
    for rel in tracked_paths:
        if rel.startswith("outputs/") and Path(rel).name != ".gitkeep":
            tracked = True
            break
    for line in status_lines:
        if line.startswith("?? "):
            path = line[3:]
            if any(path.startswith(prefix) for prefix in GENERATED_PATTERNS):
                untracked = True
                break
    return tracked, untracked


def build_payload() -> dict[str, object]:
    required_scripts_present = _exists(REQUIRED_SCRIPTS)
    required_tests_present = _exists(REQUIRED_TESTS)
    required_docs_present = _exists(REQUIRED_DOCS)
    blocker_flags = _scan_for_blockers()
    generated_artifacts_tracked, generated_artifacts_untracked_detected = _generated_artifact_flags()

    missing_scripts = [path for path in REQUIRED_SCRIPTS if path not in required_scripts_present]
    missing_tests = [path for path in REQUIRED_TESTS if path not in required_tests_present]
    missing_docs = [path for path in REQUIRED_DOCS if path not in required_docs_present]
    blocked = generated_artifacts_tracked or blocker_flags["production_db_write_detected"] or blocker_flags["scheduler_activation_detected"] or blocker_flags["data_repo_mutation_detected"]
    if missing_scripts or missing_tests or missing_docs:
        status = "EVIDENCE_INCOMPLETE"
        recommended_next_step = "Collect the missing scripts, tests, and docs evidence, then rerun the read-only preflight."
    elif blocked:
        status = "BLOCKED"
        recommended_next_step = "Remove tracked generated outputs and any production DB writer or scheduler activation from the stock ingestion path before requesting operator review."
    else:
        status = "READY_FOR_OPERATOR_REVIEW"
        recommended_next_step = "Submit the ingestion operator approval package; do not auto-enable production."

    return {
        "ingestion_production_preflight_attempted": True,
        "required_scripts_present": required_scripts_present,
        "missing_scripts": missing_scripts,
        "required_tests_present": required_tests_present,
        "missing_tests": missing_tests,
        "required_docs_present": required_docs_present,
        "missing_docs": missing_docs,
        "generated_artifacts_tracked": generated_artifacts_tracked,
        "generated_artifacts_untracked_detected": generated_artifacts_untracked_detected,
        "production_db_write_detected": blocker_flags["production_db_write_detected"],
        "scheduler_activation_detected": blocker_flags["scheduler_activation_detected"],
        "data_repo_mutation_detected": blocker_flags["data_repo_mutation_detected"],
        "vendor_call_attempted": False,
        "download_attempted": False,
        "db_write_attempted": False,
        "scheduler_activation_attempted": False,
        "production_mutation_attempted": False,
        "data_repo_mutation_attempted": False,
        "secrets_printed": False,
        "ingestion_readiness_status": status,
        "recommended_next_step": recommended_next_step,
    }


def _build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(description="Read-only production readiness preflight for Polygon/Massive stock day aggregate ingestion.")


def main(argv: list[str] | None = None) -> int:
    _build_parser().parse_args(argv)
    payload = build_payload()
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
