from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/polygon_stock_day_agg_2026_06_16_quarantine_download_execution_evidence.md")


def test_polygon_stock_day_agg_2026_06_16_quarantine_download_execution_evidence_contains_required_language() -> None:
    assert DOC_PATH.exists(), "execution evidence must exist"
    text = DOC_PATH.read_text(encoding="utf-8")

    for phrase in [
        "Implementation commit: `a02548b`",
        "Approval package commit: `f03976a`",
        "Operator approval record commit: `3841b8f`",
        "Manual vendor probe evidence commit: `89ca6da`",
        "Remaining blocker analysis commit: `4bd522b`",
        "APPROVE POLYGON STOCK DAY AGG 2026-06-16 QUARANTINE DOWNLOAD",
        "python scripts/download_polygon_stock_day_agg_single_date_quarantine.py --date 2026-06-16 --approve-local-quarantine-download --approval-phrase \"APPROVE POLYGON STOCK DAY AGG 2026-06-16 QUARANTINE DOWNLOAD\" --quarantine-dir outputs/quarantine/polygon_flat_files",
        "One-file / one-date only",
        "No parse flags",
        "No normalization flags",
        "No handoff flags",
        "No intake package flags",
        "`2026/06/2026-06-16.csv.gz`",
        "`2026-06-16.csv.gz`",
        "listed_key_sha256_prefix: `f380766d6927`",
        "resolved_key_sha256_prefix: `f380766d6927`",
        "content_length_present: true",
        "`outputs/quarantine/polygon_flat_files/polygon_stocks_day_aggs_2026-06-16.csv.gz`",
        "`local_file_exists: true`",
        "`local_file_size_bytes: 316221`",
        "`local_file_sha256: 9f40f8beb445623aa77f3a2f9fa721ae7f7fa99c27021df683bc8044f9f2b0a1`",
        "PowerShell SHA256 uppercase equivalent: `9F40F8BEB445623AA77F3A2F9FA721AE7F7FA99C27021DF683BC8044F9F2B0A1`",
        "`download_attempted: true`",
        "`remote_object_download_attempted: true`",
        "`vendor_call_attempted: true`",
        "`local_quarantine_download_enabled: true`",
        "`credentials_printed: false`",
        "`bucket_value_printed: false`",
        "`endpoint_value_printed: false`",
        "`prefix_value_printed: false`",
        "`parse_attempted: false`",
        "`normalization_attempted: false`",
        "`handoff_generation_attempted: false`",
        "`intake_package_generation_attempted: false`",
        "`db_write_attempted: false`",
        "`data_repo_mutation_attempted: false`",
        "`scheduler_activation_attempted: false`",
        "`backfill_attempted: false`",
        "`ai_wiring_attempted: false`",
        "`generated_output_commit_attempted: false`",
        "`production_mutation_attempted: false`",
        "`decompression_attempted: false`",
        "`export_attempted: false`",
        "`ingestion_attempted: false`",
        "`secrets_printed: false`",
        "`unrelated_untracked_files_staged_or_deleted: false`",
        "The downloaded `.csv.gz` file is a generated quarantine artifact and must not be committed to git.",
        "Create a parse/normalization/handoff approval package for the quarantined `2026-06-16` file.",
        "No parse, normalization, handoff, or intake generation is authorized by this evidence.",
        "No data repo staging or canonical promotion is authorized by this evidence.",
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
        "leaves the downloaded artifact uncommitted",
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
