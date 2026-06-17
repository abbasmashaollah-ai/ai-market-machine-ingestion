from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/polygon_stock_day_agg_local_handoff_writer_approval_package.md")


def test_approval_package_contains_required_operator_constraints() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    required_phrases = [
        "This document is an approval gate and does not execute anything.",
        "It does not grant production approval by itself.",
        "APPROVE POLYGON STOCK DAY AGG LOCAL HANDOFF ARTIFACT WRITE",
        "outputs/handoff_candidates/polygon_stock_day_aggs/",
        "local-only handoff artifact writer",
        "vendor calls",
        "remote downloads",
        "DB writes",
        "production mutation",
        "scheduler activation",
        "direct ai-market-machine-data repo mutation",
        "API route creation",
        "warehouse writer creation",
        "ingestion activation",
        "committing quarantine vendor data",
        "safe JSON output",
        "no secrets printed",
        "no full object keys printed",
        "source file hash included",
        "record counts included",
        "no DB credentials required",
        "default no-approval blocks",
        "wrong approval phrase blocks",
        "approved local fixture writes only a local artifact",
        "malformed rows rejected safely",
        "no vendor, download, DB, scheduler, or production flags are true",
        "quarantine file is never committed",
        "implement the local-only handoff artifact writer under the allowed output path",
        "still no DB writes or production mutation",
    ]

    for phrase in required_phrases:
        assert phrase in text
