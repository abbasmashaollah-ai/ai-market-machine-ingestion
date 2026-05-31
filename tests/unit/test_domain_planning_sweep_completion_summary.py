from __future__ import annotations

from pathlib import Path


def test_summary_doc_exists_and_mentions_required_items():
    text = Path("docs/domain_planning_sweep_completion_summary.md").read_text(encoding="utf-8").lower()
    for needle in [
        "planning sweep is complete",
        "symbol master",
        "etf/index universe",
        "ohlcv",
        "fred macro",
        "volatility indexes",
        "event calendar / earnings",
        "fundamentals/filings",
        "news/sentiment",
        "cross-asset ohlcv",
        "breadth/participation",
        "options",
        "flows/positioning",
        "vertical-slice plan",
        "source plan",
        "dry-run foundation",
        "preflight",
        "evidence plan",
        "readiness summary",
        "manual inventory wiring",
        "ohlcv manual spine",
        "symbol master initial polygon population",
        "etf/index universe",
        "fred macro",
        "opex deterministic calendar",
        "volatility indexes blocked by polygon entitlement",
        "data-side contracts",
        "live adapters",
        "persistence writers",
        "evidence verifiers",
        "scheduler activation only after proven manual paths",
        "no ai/trading/risk/signal/regime/portfolio logic",
        "no unapproved db writes",
        "no schema ownership in ingestion",
    ]:
        assert needle in text


def test_future_build_order_marks_sweep_complete_and_next_phase():
    text = Path("docs/future_domain_build_order.md").read_text(encoding="utf-8").lower()
    assert "domain planning sweep complete" in text
    assert "next phase: data-side contract prioritization" in text
    assert "event calendar if continuing the event domain" in text
    assert "news/sentiment if product-facing feed is priority" in text
    assert "fundamentals/filings if ticker analyzer depth is priority" in text
    assert "cross-asset ohlcv if market regime coverage is priority" in text


def test_boundary_language_present():
    text = Path("docs/domain_planning_sweep_completion_summary.md").read_text(encoding="utf-8").lower()
    assert "no ai/trading/risk/signal/regime/portfolio logic" in text
    assert "no unapproved db writes" in text
    assert "no schema ownership in ingestion" in text
