from __future__ import annotations

from pathlib import Path


def test_readiness_summary_exists_and_mentions_required_items():
    text = Path("docs/fundamentals_filings_readiness_summary.md").read_text(encoding="utf-8").lower()
    for needle in [
        "vertical-slice plan exists",
        "source plan exists",
        "fixture-backed dry-run foundation exists",
        "preflight exists",
        "evidence plan exists",
        "manual inventory includes fundamentals/filings commands",
        "company_profile",
        "financial_statement",
        "financial_metric",
        "earnings_estimate",
        "sec_filing",
        "symbol_master",
        "sec",
        "fmp",
        "finnhub",
        "manual_fixture",
        "live vendor adapters are not built yet",
        "data-side contracts are not yet approved",
        "persistence is deferred",
        "no db reads or db writes are enabled",
        "data-side contracts for the record families",
        "sec live dry-run planning",
        "fmp fundamentals live dry-run planning",
    ]:
        assert needle in text


def test_future_build_order_pauses_fundamentals_filings_and_moves_news_next():
    text = Path("docs/future_domain_build_order.md").read_text(encoding="utf-8").lower()
    assert "fundamentals/filings" in text
    assert "paused at readiness checkpoint" in text
    assert "persistence deferred until the approved data-side contract exists" in text
    assert "news/sentiment" in text


def test_boundary_language_present():
    text = Path("docs/fundamentals_filings_readiness_summary.md").read_text(encoding="utf-8").lower()
    assert "producer-planning side only" in text
    assert "no ai/trading/risk/signal/regime/portfolio logic" in text
