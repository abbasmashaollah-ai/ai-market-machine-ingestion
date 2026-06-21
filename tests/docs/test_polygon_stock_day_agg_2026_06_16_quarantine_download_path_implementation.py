from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/polygon_stock_day_agg_2026_06_16_quarantine_download_path_implementation.md")


def test_polygon_stock_day_agg_2026_06_16_quarantine_download_path_implementation_contains_required_language() -> None:
    assert DOC_PATH.exists(), "implementation doc must exist"
    text = DOC_PATH.read_text(encoding="utf-8")

    for phrase in [
        "Blocker commit: `0c7ae7a`",
        "Approval package commit: `f03976a`",
        "Operator approval record commit: `3841b8f`",
        "Manual probe evidence commit: `89ca6da`",
        "APPROVE POLYGON STOCK DAY AGG 2026-06-16 QUARANTINE DOWNLOAD",
        "generic approval phrase `APPROVE POLYGON FLAT FILE SINGLE DATE LOCAL QUARANTINE DOWNLOAD`",
        "The approved stock-day phrase `APPROVE POLYGON STOCK DAY AGG 2026-06-16 QUARANTINE DOWNLOAD` did not match",
        "Added a stock-day-specific wrapper script: `scripts/download_polygon_stock_day_agg_single_date_quarantine.py`",
        "support in the generic downloader for an injected required approval phrase",
        "Enforced one-date-only behavior for `2026-06-16`",
        "output path fixed to `outputs/quarantine/polygon_flat_files/polygon_stocks_day_aggs_2026-06-16.csv.gz`",
        "Future Approved Command",
        "No parse",
        "No normalization",
        "No handoff candidate generation",
        "No intake package generation",
        "No DB write",
        "No data repo mutation",
        "No scheduler activation",
        "No backfill",
        "No AI wiring",
        "No generated output commit",
        "Unrelated untracked files remain untouched",
        "No live download was executed by this implementation step.",
        "The next step is live one-date quarantine download execution evidence for `2026-06-16`",
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
