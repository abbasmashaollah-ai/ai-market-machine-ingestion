from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/polygon_stock_day_agg_2026_06_16_parse_normalize_handoff_approval_package.md")


def test_polygon_stock_day_agg_2026_06_16_parse_normalize_handoff_approval_package_contains_required_language() -> None:
    assert DOC_PATH.exists(), "approval package must exist"
    text = DOC_PATH.read_text(encoding="utf-8")

    for phrase in [
        "Quarantine download evidence commit: `d4b4896`",
        "Local quarantine path: `outputs/quarantine/polygon_flat_files/polygon_stocks_day_aggs_2026-06-16.csv.gz`",
        "Size_bytes: `316221`",
        "Sha256: `9f40f8beb445623aa77f3a2f9fa721ae7f7fa99c27021df683bc8044f9f2b0a1`",
        "`outputs/handoff_candidates/polygon_stock_day_aggs/polygon_stock_day_aggs_2026-06-16_rows.jsonl`",
        "`outputs/handoff_candidates/polygon_stock_day_aggs/polygon_stock_day_aggs_2026-06-16_summary.json`",
        "`outputs/handoff_candidates/polygon_stock_day_aggs/polygon_stock_day_aggs_batch_2026-06-16_2026-06-16_manifest.json`",
        "`outputs/intake_packages/polygon_stock_day_aggs/polygon_stock_day_aggs_2026-06-16_2026-06-16_intake_package.json`",
        "APPROVE POLYGON STOCK DAY AGG 2026-06-16 PARSE NORMALIZE HANDOFF",
        "Operator Approval Record Template",
        "Required Post-Execution Evidence",
        "No vendor call confirmation",
        "No download confirmation",
        "No DB write confirmation",
        "No data repo mutation confirmation",
        "No scheduler/backfill confirmation",
        "No AI wiring confirmation",
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
        "Create operator approval record",
        "After approval, execute parse, normalize, and handoff generation",
        "After handoff package exists, move to `ai-market-machine-data` intake validation approval",
        "approval intent only",
        "does not execute parse, normalize, or handoff actions",
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
