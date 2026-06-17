from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/polygon_stock_day_agg_existing_quarantine_file_evidence.md")


def test_existing_quarantine_file_evidence_contains_required_language() -> None:
    assert DOC_PATH.exists()
    text = DOC_PATH.read_text(encoding="utf-8")

    for phrase in [
        "This is evidence only, not new approval.",
        "No re-download was performed.",
        "path: `outputs/quarantine/polygon_flat_files/polygon_stocks_day_aggs_2026-06-15.csv.gz`",
        "local file exists: `true`",
        "local size: `317857`",
        "listed expected size: `317857`",
        "local sha256: `ac71addad2e0ba969b76763585e7e15fc74660a13c80d31869b5cbf787df3682`",
        "date: `2026-06-15`",
        "key tail: `2026/06/2026-06-15.csv.gz`",
        "filename: `polygon_stocks_day_aggs_2026-06-15.csv.gz`",
        "The approved Gate 2 document uses the internal script phrase:",
        "APPROVE POLYGON FLAT FILE SINGLE DATE LOCAL QUARANTINE DOWNLOAD",
        "The Gate 2 approval record document used a different human-facing phrase:",
        "APPROVE POLYGON STOCK DAY AGG QUARANTINE DOWNLOAD",
        "no overwrite performed",
        "no vendor call performed by this evidence step",
        "no download performed by this evidence step",
        "no parse performed",
        "no decompression performed",
        "no handoff artifact generated",
        "no intake descriptor generated",
        "no data repo mutation",
        "no DB write",
        "no scheduler activation",
        "no secrets printed",
        "The next step is parse/normalize/handoff generation from the existing approved quarantine file.",
    ]:
        assert phrase in text
