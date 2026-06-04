from __future__ import annotations

from pathlib import Path


def test_market_feature_bundle_fixture_mode_checkpoint_mentions_current_contract() -> None:
    text = Path("docs/market_feature_bundle_fixture_mode_checkpoint.md").read_text(encoding="utf-8")

    for token in (
        "prices",
        "breadth",
        "sector_rotation",
        "cross_asset",
        "liquidity_rates",
        "volatility",
        "event_calendar",
        "news_sentiment",
        "fundamentals",
        "flows_positioning",
        "options",
        "earnings",
        "macro_liquidity",
        "market_risk",
        "market_regime",
        "Build the raw/domain bundle.",
        "Build the compact summary from the raw/domain bundle.",
        "Run `macro_liquidity` and append it.",
        "Run `market_risk` and append it.",
        "Run `market_regime` and append it.",
        "total_warnings == 0",
        "safety flags are true",
        "rejected counts are zero",
        "CLI summary-only output works",
        "validator passes",
        "no DB writes",
        "no vendor calls",
        "no live API calls",
        "no LLM calls",
        "no scheduler activation",
        "AI Machine consumption last",
    ):
        assert token in text

