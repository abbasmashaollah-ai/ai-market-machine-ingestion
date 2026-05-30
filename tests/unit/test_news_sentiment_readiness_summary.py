from __future__ import annotations

from pathlib import Path


def test_readiness_summary_exists_and_mentions_required_items():
    text = Path("docs/news_sentiment_readiness_summary.md").read_text(encoding="utf-8").lower()
    for needle in [
        "vertical-slice plan exists",
        "source plan exists",
        "fixture-backed dry-run foundation exists",
        "preflight exists",
        "evidence plan exists",
        "manual inventory includes news/sentiment commands",
        "news_id",
        "published_at",
        "source",
        "publisher",
        "title",
        "summary",
        "url",
        "tickers",
        "sentiment_label",
        "sentiment_score",
        "raw_source_id",
        "notes",
        "symbol_master",
        "finnhub",
        "fmp",
        "polygon",
        "manual_fixture",
        "live vendor adapters are not built yet",
        "data-side contracts are not yet approved",
        "persistence is deferred",
        "no db reads or db writes are enabled",
        "data-side news/sentiment contract",
        "finnhub live dry-run planning",
        "fmp news live dry-run planning",
    ]:
        assert needle in text


def test_future_build_order_pauses_news_sentiment_and_moves_cross_asset_next():
    text = Path("docs/future_domain_build_order.md").read_text(encoding="utf-8").lower()
    assert "news/sentiment" in text
    assert "paused at readiness checkpoint" in text
    assert "persistence deferred until the approved data-side contract exists" in text
    assert "cross-asset ohlcv" in text


def test_boundary_language_present():
    text = Path("docs/news_sentiment_readiness_summary.md").read_text(encoding="utf-8").lower()
    assert "producer-planning side only" in text
    assert "no ai/trading/risk/signal/regime/portfolio logic" in text
