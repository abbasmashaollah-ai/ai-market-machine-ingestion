from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/polygon_stock_day_agg_2026_06_16_quarantine_download_operator_approval_record.md")


def test_polygon_stock_day_agg_2026_06_16_quarantine_download_operator_approval_record_contains_required_approval_scope_and_safety() -> None:
    assert DOC_PATH.exists(), "approval record must exist"
    text = DOC_PATH.read_text(encoding="utf-8")

    for phrase in [
        "APPROVE POLYGON STOCK DAY AGG 2026-06-16 QUARANTINE DOWNLOAD",
        "Approval package commit: `f03976a`",
        "Manual probe evidence commit: `89ca6da`",
        "Approver: Abbas Mashaollah",
        "Target date: `2026-06-16`",
        "Expected filename: `2026-06-16.csv.gz`",
        "Redacted key tail: `2026/06/2026-06-16.csv.gz`",
        "Destination: `outputs/quarantine/polygon_flat_files/polygon_stocks_day_aggs_2026-06-16.csv.gz`",
        "Probe size comparison",
        "Required Post-Download Evidence",
        "No parse confirmation",
        "No normalization confirmation",
        "No handoff/intake generation confirmation",
        "No DB write confirmation",
        "No scheduler/backfill confirmation",
        "No AI wiring confirmation",
        "No secrets printed confirmation",
        "Unrelated untracked files untouched",
        "Parsing",
        "Normalization",
        "Handoff candidate generation",
        "Intake package generation",
        "Data repo mutation",
        "DB write",
        "Production staging load",
        "Canonical promotion",
        "Scheduler/backfill",
        "AI wiring",
        "Generated output commit",
        "Unrelated untracked file staging/deletion",
        "Printing secrets or DB URLs",
        "Operator approval record created",
        "Quarantine download approved for future execution",
        "Quarantine download not executed by this commit",
        "No parse/normalization/handoff/data repo mutation",
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

