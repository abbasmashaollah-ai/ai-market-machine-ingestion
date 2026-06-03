"""Builder for dry-run news sentiment observations."""

from __future__ import annotations

from datetime import datetime, timezone

from .news_sentiment_engine import (
    calculate_average_score,
    calculate_narrative_pressure_score,
    calculate_weighted_sentiment_score,
    count_articles_by_category,
    count_articles_by_sentiment,
    count_high_impact_articles,
    determine_sentiment_regime_label,
    filter_articles_by_lookback,
    get_top_symbols_by_relevance,
)


def _normalize_timestamp(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    return str(value)


def _normalize_observation_datetime(observation_date, timestamp):
    if isinstance(timestamp, datetime):
        return timestamp.astimezone(timezone.utc)
    if isinstance(timestamp, str) and timestamp:
        text = timestamp.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(text)
        except ValueError:
            parsed = None
        if parsed is not None:
            return parsed.astimezone(timezone.utc) if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    if isinstance(observation_date, datetime):
        return observation_date.astimezone(timezone.utc)
    if isinstance(observation_date, str) and observation_date:
        try:
            parsed = datetime.fromisoformat(observation_date)
        except ValueError:
            parsed = None
        if parsed is not None:
            if parsed.tzinfo is None:
                return parsed.replace(hour=16, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)
    return datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc)


def build_news_sentiment_observation(articles, observation_date, timestamp=None, lookback_hours=24, source="fixture_news"):
    normalized_timestamp = _normalize_timestamp(timestamp)
    observation_datetime = _normalize_observation_datetime(observation_date, timestamp)
    filtered_articles = filter_articles_by_lookback(articles, observation_datetime, lookback_hours)

    sentiment_counts = count_articles_by_sentiment(filtered_articles)
    category_counts = count_articles_by_category(filtered_articles)
    high_impact_article_count = count_high_impact_articles(filtered_articles)
    macro_article_count = int(category_counts.get("MACRO", 0) or 0) + int(category_counts.get("FED", 0) or 0)
    earnings_article_count = int(category_counts.get("EARNINGS", 0) or 0)
    fed_article_count = int(category_counts.get("FED", 0) or 0)
    geopolitical_article_count = int(category_counts.get("GEOPOLITICAL", 0) or 0)
    sector_article_count = int(category_counts.get("SECTOR", 0) or 0)
    company_article_count = int(category_counts.get("COMPANY", 0) or 0)
    average_sentiment_score = calculate_average_score(filtered_articles, "sentiment_score")
    average_relevance_score = calculate_average_score(filtered_articles, "relevance_score")
    average_impact_score = calculate_average_score(filtered_articles, "impact_score")
    weighted_sentiment_score = calculate_weighted_sentiment_score(filtered_articles)
    narrative_pressure_score = calculate_narrative_pressure_score(filtered_articles)
    high_impact_negative_count = sum(
        1
        for article in filtered_articles
        if isinstance(article, dict)
        and float(article.get("sentiment_score", 0) or 0) <= -0.2
        and float(article.get("impact_score", 0) or 0) >= 0.75
    )
    high_impact_positive_count = sum(
        1
        for article in filtered_articles
        if isinstance(article, dict)
        and float(article.get("sentiment_score", 0) or 0) >= 0.2
        and float(article.get("impact_score", 0) or 0) >= 0.75
    )
    sentiment_regime_label = determine_sentiment_regime_label(
        weighted_sentiment_score=weighted_sentiment_score,
        high_impact_negative_count=high_impact_negative_count,
        high_impact_positive_count=high_impact_positive_count,
        article_count=len(filtered_articles),
    )
    return {
        "observation_date": str(observation_date),
        "timestamp": normalized_timestamp,
        "lookback_hours": int(lookback_hours),
        "articles": [dict(article) for article in filtered_articles],
        "article_count": len(filtered_articles),
        "positive_article_count": sentiment_counts.get("positive", 0),
        "negative_article_count": sentiment_counts.get("negative", 0),
        "neutral_article_count": sentiment_counts.get("neutral", 0),
        "high_impact_article_count": high_impact_article_count,
        "macro_article_count": macro_article_count,
        "earnings_article_count": earnings_article_count,
        "fed_article_count": fed_article_count,
        "geopolitical_article_count": geopolitical_article_count,
        "sector_article_count": sector_article_count,
        "company_article_count": company_article_count,
        "average_sentiment_score": average_sentiment_score,
        "average_relevance_score": average_relevance_score,
        "average_impact_score": average_impact_score,
        "weighted_sentiment_score": weighted_sentiment_score,
        "narrative_pressure_score": narrative_pressure_score,
        "sentiment_regime_label": sentiment_regime_label,
        "top_symbols": get_top_symbols_by_relevance(filtered_articles, top_n=5),
        "source": source,
        "quality_status": "PENDING",
        "certification_status": "PENDING",
        "freshness_status": "PENDING",
        "lineage": {},
        "evidence": {},
        "no_db_writes": True,
        "no_vendor_calls": True,
        "no_scheduler_activation": True,
    }
