from datetime import datetime, timezone

from app.features.news_sentiment.news_sentiment_engine import (
    calculate_average_score,
    calculate_narrative_pressure_score,
    calculate_weighted_sentiment_score,
    classify_sentiment_bucket,
    count_articles_by_category,
    count_articles_by_sentiment,
    count_high_impact_articles,
    determine_sentiment_regime_label,
    filter_articles_by_lookback,
    get_top_symbols_by_relevance,
    normalize_news_category,
)


def test_normalization_and_lookback_filtering() -> None:
    observation_datetime = datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc)
    articles = [
        {"published_at": "2026-01-15T14:00:00Z", "category": "fed"},
        {"published_at": "2026-01-14T14:00:00Z", "category": "macro"},
    ]
    filtered = filter_articles_by_lookback(articles, observation_datetime, 24)
    assert len(filtered) == 1
    assert normalize_news_category("fed") == "FED"
    assert normalize_news_category("unknown") == "OTHER"


def test_sentiment_buckets_and_counts() -> None:
    articles = [
        {"sentiment_score": 0.6, "category": "FED", "impact_score": 0.8, "relevance_score": 0.9, "symbols": ["SPY"]},
        {"sentiment_score": -0.5, "category": "EARNINGS", "impact_score": 0.9, "relevance_score": 0.7, "symbols": ["AAPL"]},
        {"sentiment_score": 0.0, "category": "SECTOR", "impact_score": 0.2, "relevance_score": 0.3, "symbols": ["MSFT"]},
    ]
    assert classify_sentiment_bucket(0.6) == "POSITIVE"
    assert classify_sentiment_bucket(-0.5) == "NEGATIVE"
    assert classify_sentiment_bucket(0.0) == "NEUTRAL"
    assert count_articles_by_sentiment(articles) == {"positive": 1, "negative": 1, "neutral": 1}
    assert count_articles_by_category(articles)["FED"] == 1
    assert count_high_impact_articles(articles, threshold=0.75) == 2


def test_average_weighted_and_pressure_scores() -> None:
    articles = [
        {"sentiment_score": 0.5, "relevance_score": 0.8, "impact_score": 0.9, "symbols": ["SPY", "QQQ"]},
        {"sentiment_score": -0.2, "relevance_score": 0.6, "impact_score": 0.7, "symbols": ["AAPL"]},
    ]
    assert calculate_average_score(articles, "sentiment_score") == 0.15
    weighted = calculate_weighted_sentiment_score(articles)
    assert weighted is not None
    assert calculate_narrative_pressure_score(articles) is not None
    assert get_top_symbols_by_relevance(articles, top_n=2) == ["SPY", "QQQ"]


def test_sentiment_labels() -> None:
    assert determine_sentiment_regime_label(article_count=0) == "INSUFFICIENT_DATA"
    assert determine_sentiment_regime_label(weighted_sentiment_score=0.3, high_impact_positive_count=2, article_count=3) == "HIGH_IMPACT_POSITIVE"
    assert determine_sentiment_regime_label(weighted_sentiment_score=-0.3, high_impact_negative_count=2, article_count=3) == "HIGH_IMPACT_NEGATIVE"
    assert determine_sentiment_regime_label(weighted_sentiment_score=0.2, article_count=3) == "POSITIVE_SENTIMENT"
    assert determine_sentiment_regime_label(weighted_sentiment_score=-0.2, article_count=3) == "NEGATIVE_SENTIMENT"
