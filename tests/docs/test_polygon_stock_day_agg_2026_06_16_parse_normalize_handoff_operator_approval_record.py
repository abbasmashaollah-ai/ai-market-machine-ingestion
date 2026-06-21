from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/polygon_stock_day_agg_2026_06_16_parse_normalize_handoff_operator_approval_record.md")


def test_polygon_stock_day_agg_2026_06_16_parse_normalize_handoff_operator_approval_record_contains_required_language() -> None:
    assert DOC_PATH.exists(), "approval record must exist"
    text = DOC_PATH.read_text(encoding="utf-8")

    for phrase in [
        "APPROVE POLYGON STOCK DAY AGG 2026-06-16 PARSE NORMALIZE HANDOFF",
        "Approval package commit: `5d15d08`",
        "Quarantine download evidence commit: `d4b4896`",
        "Approver: Abbas Mashaollah",
        "Path: `outputs/quarantine/polygon_flat_files/polygon_stocks_day_aggs_2026-06-16.csv.gz`",
        "Size_bytes: `316221`",
        "Sha256: `9f40f8beb445623aa77f3a2f9fa721ae7f7fa99c27021df683bc8044f9f2b0a1`",
        "`outputs/handoff_candidates/polygon_stock_day_aggs/polygon_stock_day_aggs_2026-06-16_rows.jsonl`",
        "`outputs/handoff_candidates/polygon_stock_day_aggs/polygon_stock_day_aggs_2026-06-16_summary.json`",
        "`outputs/handoff_candidates/polygon_stock_day_aggs/polygon_stock_day_aggs_batch_2026-06-16_2026-06-16_manifest.json`",
        "`outputs/intake_packages/polygon_stock_day_aggs/polygon_stock_day_aggs_2026-06-16_2026-06-16_intake_package.json`",
        "Required Post-Execution Evidence",
        "No vendor call confirmation",
        "No download confirmation",
        "No DB write confirmation",
        "No data repo mutation confirmation",
        "No scheduler/backfill confirmation",
        "No AI wiring confirmation",
        "Secrets not printed",
        "Generated outputs left uncommitted unless separately approved",
        "Vendor call/listing/probe",
        "Remote file read",
        "Download",
        "DB write",
        "Data repo mutation",
        "Production staging load",
        "Canonical promotion",
        "Scheduler/backfill",
        "AI wiring",
        "Committing generated output artifacts",
        "Staging or deleting unrelated untracked files",
        "Printing secrets or DB URLs",
        "Operator approval record created",
        "Parse/normalize/handoff execution approved for future execution",
        "Parse/normalize/handoff not executed by this commit",
        "Data repo intake not executed by this commit",
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
