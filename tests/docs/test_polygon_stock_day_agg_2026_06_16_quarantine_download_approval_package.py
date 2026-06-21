from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/polygon_stock_day_agg_2026_06_16_quarantine_download_approval_package.md")


def test_polygon_stock_day_agg_2026_06_16_quarantine_download_approval_package_contains_required_scope_and_safety() -> None:
    assert DOC_PATH.exists(), "approval package must exist"
    text = DOC_PATH.read_text(encoding="utf-8")

    for phrase in [
        "Request approval to download the confirmed `2026-06-16` Polygon stock day aggregate file into local quarantine only.",
        "Manual probe evidence commit: `89ca6da`",
        "`object_present true`",
        "`redacted_key_tail 2026/06/2026-06-16.csv.gz`",
        "`size_bytes 316221`",
        "`listed_key_sha256_prefix a988421953a6`",
        "`resolved_key_sha256_prefix a988421953a6`",
        "No prior download occurred",
        "One file only",
        "Date: `2026-06-16`",
        "Dataset type: `daily_ohlcv`",
        "Source: Polygon/Massive flat files",
        "Destination: local quarantine path only",
        "Compute local file hash and size after download",
        "Write/download evidence doc only after operator-approved execution",
        "`outputs/quarantine/polygon_flat_files/polygon_stocks_day_aggs_2026-06-16.csv.gz`",
        "APPROVE POLYGON STOCK DAY AGG 2026-06-16 QUARANTINE DOWNLOAD",
        "Operator Approval Record Template",
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
        "After this approval package, create an operator approval record",
        "Only after approval record, execute one quarantine download",
        "After download evidence, create parse/normalization/handoff approval package",
    ]:
        assert phrase in text

    assert "89ca6da" in text

    lowered = text.lower()
    for forbidden in [
        "postgresql://",
        "postgresql+psycopg2://",
        "password=",
        "token=",
        "api key=",
    ]:
        assert forbidden not in lowered
