from __future__ import annotations

from pathlib import Path


def test_fundamentals_filings_vertical_slice_plan_exists_and_mentions_required_terms():
    plan = Path(__file__).resolve().parents[2] / "docs" / "fundamentals_filings_vertical_slice_plan.md"
    text = plan.read_text(encoding="utf-8").lower()

    assert plan.exists()
    for needle in [
        "purpose",
        "company profile",
        "financial statements",
        "ratios/metrics",
        "earnings estimates",
        "sec filings",
        "symbol_master",
        "sec",
        "fmp",
        "finnhub",
        "manual_fixture",
        "company_profile",
        "financial_statement",
        "financial_metric",
        "earnings_estimate",
        "sec_filing",
        "quality expectations",
        "lineage expectations",
        "preflight/runner/evidence pattern",
        "persistence deferred until data-side contracts are approved",
        "no ai/trading/risk/signal/regime/portfolio logic",
    ]:
        assert needle in text
