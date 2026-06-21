from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/polygon_stock_day_agg_vendor_probe_environment_readiness_execution_evidence.md")


def test_polygon_stock_day_agg_vendor_probe_environment_readiness_execution_evidence_contains_required_scope_and_safety() -> None:
    assert DOC_PATH.exists(), "execution evidence must exist"
    text = DOC_PATH.read_text(encoding="utf-8")

    for phrase in [
        "Approval package commit: `02da11c`",
        "Operator approval record commit: `0ab6b83`",
        "Environment readiness success evidence commit: `3bbecb3`",
        "Readiness checker returned `readiness_passed true` and `safe_to_retry_probe true` before probe: not satisfied in the current execution attempt",
        "python scripts/preflight_polygon_flat_file_manifest.py --enable-remote-listing --start-date 2026-06-16 --end-date 2026-06-16 --max-days 1",
        "Listing/probe-only mode",
        "No download flags",
        "No output/write flags",
        "Target date checked: `2026-06-16`",
        "Vendor object/key/path checked: not available because remote listing did not execute",
        "Availability result: probe blocked safely before remote object access",
        "Metadata if available: not available",
        "Polygon flat-file configuration and `boto3` were unavailable in this environment",
        "`vendor_call_attempted false`",
        "`remote_listing_attempted false`",
        "`download_attempted false`",
        "`file_write_attempted false`",
        "`quarantine_write_attempted false`",
        "`parse_attempted false`",
        "`normalization_attempted false`",
        "`handoff_generation_attempted false`",
        "`intake_package_generation_attempted false`",
        "`db_write_attempted false`",
        "`data_repo_mutation_attempted false`",
        "`scheduler_activation_attempted false`",
        "`backfill_attempted false`",
        "`ai_wiring_attempted false`",
        "`secrets_printed false`",
        "`unrelated_untracked_files_staged_or_deleted false`",
        "`probe_blocked_safely`",
        "Fix environment readiness, then rerun readiness before another probe attempt",
        "If a file becomes available, create a separate quarantine download approval package",
        "No download is authorized by this evidence",
        "Download",
        "Quarantine write",
        "Parse/normalization",
        "Handoff/intake generation",
        "DB write",
        "Data repo mutation",
        "Scheduler/backfill",
        "AI wiring",
        "Generated output commit",
        "Unrelated untracked file staging/deletion",
        "Secrets printed",
    ]:
        assert phrase in text

    lowered = text.lower()
    for forbidden in [
        "postgresql://",
        "postgresql+psycopg2://",
        "password=",
        "token=",
        "api key=",
    ]:
        assert forbidden not in lowered
