from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/polygon_stock_day_agg_2026_06_16_quarantine_download_blocker_evidence.md")


def test_polygon_stock_day_agg_2026_06_16_quarantine_download_blocker_evidence_contains_required_language() -> None:
    assert DOC_PATH.exists(), "blocker evidence must exist"
    text = DOC_PATH.read_text(encoding="utf-8")

    for phrase in [
        "Approval package commit: `f03976a`",
        "Operator approval record commit: `3841b8f`",
        "Manual probe evidence commit: `89ca6da`",
        "APPROVE POLYGON STOCK DAY AGG 2026-06-16 QUARANTINE DOWNLOAD",
        "python scripts/download_polygon_flat_file_single_date_quarantine.py --date 2026-06-16 --approve-local-quarantine-download --approval-phrase \"APPROVE POLYGON FLAT FILE SINGLE DATE LOCAL QUARANTINE DOWNLOAD\" --quarantine-dir outputs/quarantine/polygon_flat_files",
        "One-file / one-date only",
        "No parse flags",
        "No normalization flags",
        "No handoff flags",
        "No intake package flags",
        "`2026/06/2026-06-16.csv.gz`",
        "`2026-06-16.csv.gz`",
        "Probe size_bytes: `316221`",
        "Listed key sha256 prefix: `a988421953a6`",
        "Resolved key sha256 prefix: `a988421953a6`",
        "Outcome: `access_denied_or_config_error`",
        "`vendor_call_attempted true`",
        "`remote_file_read_attempted false`",
        "`download_attempted false`",
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
        "`generated_output_commit_attempted false`",
        "`credentials_printed false`",
        "`secrets_printed false`",
        "`unrelated_untracked_files_staged_or_deleted false`",
        "Local quarantine path: `outputs/quarantine/polygon_flat_files/polygon_stocks_day_aggs_2026-06-16.csv.gz`",
        "Local file exists: `false`",
        "Local size_bytes: `0`",
        "Expected/probe size comparison: not available because the utility blocked safely before download",
        "Create a parse/normalization/handoff approval package only after a successful quarantine download exists",
        "No parse, normalization, handoff, or data repo action is authorized by this evidence",
        "Parse",
        "Normalization",
        "Handoff candidate generation",
        "Intake package generation",
        "DB write",
        "Data repo mutation",
        "Production staging load",
        "Canonical promotion",
        "Scheduler/backfill",
        "AI wiring",
        "Committing generated quarantine/output artifact",
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
