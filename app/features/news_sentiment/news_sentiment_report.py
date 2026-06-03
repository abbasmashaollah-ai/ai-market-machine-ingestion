"""Report helpers for news sentiment dry-run outputs."""

from __future__ import annotations

from collections.abc import Mapping


def build_news_sentiment_report(observation, writer_result=None):
    payload = dict(observation or {})
    report = {
        "observation_date": payload.get("observation_date"),
        "timestamp": payload.get("timestamp"),
        "lookback_hours": payload.get("lookback_hours"),
        "article_count": payload.get("article_count"),
        "positive_article_count": payload.get("positive_article_count"),
        "negative_article_count": payload.get("negative_article_count"),
        "neutral_article_count": payload.get("neutral_article_count"),
        "high_impact_article_count": payload.get("high_impact_article_count"),
        "macro_article_count": payload.get("macro_article_count"),
        "earnings_article_count": payload.get("earnings_article_count"),
        "fed_article_count": payload.get("fed_article_count"),
        "geopolitical_article_count": payload.get("geopolitical_article_count"),
        "sector_article_count": payload.get("sector_article_count"),
        "company_article_count": payload.get("company_article_count"),
        "average_sentiment_score": payload.get("average_sentiment_score"),
        "average_relevance_score": payload.get("average_relevance_score"),
        "average_impact_score": payload.get("average_impact_score"),
        "weighted_sentiment_score": payload.get("weighted_sentiment_score"),
        "narrative_pressure_score": payload.get("narrative_pressure_score"),
        "sentiment_regime_label": payload.get("sentiment_regime_label"),
        "top_symbols": list(payload.get("top_symbols") or []),
        "safety_flags": {
            "no_db_writes": bool(payload.get("no_db_writes") is True),
            "no_vendor_calls": bool(payload.get("no_vendor_calls") is True),
            "no_scheduler_activation": bool(payload.get("no_scheduler_activation") is True),
        },
    }
    if writer_result is not None:
        report["accepted_count"] = getattr(writer_result, "accepted_count", None)
        report["rejected_count"] = getattr(writer_result, "rejected_count", None)
    return report
