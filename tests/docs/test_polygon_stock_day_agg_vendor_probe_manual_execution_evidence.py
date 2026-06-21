from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/polygon_stock_day_agg_vendor_probe_manual_execution_evidence.md")


def test_polygon_stock_day_agg_vendor_probe_manual_execution_evidence_contains_required_scope_and_safety() -> None:
    assert DOC_PATH.exists(), "manual execution evidence must exist"
    text = DOC_PATH.read_text(encoding="utf-8")

    for phrase in [
        "Record manual operator-run vendor listing/probe evidence for `2026-06-16`.",
        "Manual PowerShell session",
        "Codex environment did not inherit local environment",
        "Earlier Codex blocker commit: `406a827`",
        "This manual evidence supersedes the blocked Codex execution for environment-specific probe status",
        "Readiness checker returned `readiness_passed true`",
        "Readiness checker returned `safe_to_retry_probe true`",
        "Required config key names were present",
        "Only key names were documented; no values",
        "`python scripts/preflight_polygon_flat_file_manifest.py --enable-remote-listing --start-date 2026-06-16 --end-date 2026-06-16 --max-days 1`",
        "Listing/probe-only",
        "No download flags",
        "No write flags",
        "No parse/normalization/handoff flags",
        "`object_present true`",
        "Date: `2026-06-16`",
        "`redacted_key_tail 2026/06/2026-06-16.csv.gz`",
        "`remote_list_expected_filename 2026-06-16.csv.gz`",
        "`size_bytes 316221`",
        "`etag_present true`",
        "`last_modified_present true`",
        "`listed_key_sha256_prefix a988421953a6`",
        "`resolved_key_sha256_prefix a988421953a6`",
        "Outcome: `file_available_for_future_download_approval`",
        "`vendor_call_attempted true`",
        "`remote_object_list_attempted true`",
        "`remote_file_read_attempted false`",
        "`download_attempted false`",
        "`export_attempted false`",
        "`db_write_attempted false`",
        "`ingestion_attempted false`",
        "`scheduler_activation_attempted false`",
        "`production_mutation_attempted false`",
        "`production_handoff_generation_authorized false`",
        "`credentials_printed false`",
        "`bucket_value_printed false`",
        "`endpoint_value_printed false`",
        "`prefix_value_printed false`",
        "No secrets printed",
        "Unrelated untracked files were not staged or deleted",
        "Create a separate quarantine download approval package for the available `2026-06-16` file",
        "No download is authorized by this evidence",
        "No remote file read is authorized by this evidence",
        "No parse/normalization/handoff/intake generation is authorized by this evidence",
        "No data repo staging/canonical promotion is authorized by this evidence",
        "Download",
        "Quarantine write",
        "Parse/normalization",
        "Handoff generation",
        "Intake package generation",
        "DB write",
        "Data repo mutation",
        "Production staging load",
        "Canonical promotion",
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
