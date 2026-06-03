import json
from datetime import datetime, timezone

from app.features.news_sentiment.news_sentiment_builder import build_news_sentiment_observation
from tests.fixtures.news_sentiment_articles import build_news_sentiment_articles_scenario


def test_observation_contains_expected_fields() -> None:
    articles = build_news_sentiment_articles_scenario("mixed_market")
    observation = build_news_sentiment_observation(articles, "2026-01-15", timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc))
    assert observation["observation_date"] == "2026-01-15"
    assert observation["lookback_hours"] == 24
    assert observation["article_count"] >= 1
    assert observation["sentiment_regime_label"]
    assert observation["top_symbols"]
    assert observation["quality_status"] == "PENDING"
    assert observation["certification_status"] == "PENDING"
    assert observation["freshness_status"] == "PENDING"
    json.dumps(observation)


def test_observation_filters_outside_lookback() -> None:
    articles = build_news_sentiment_articles_scenario("low_signal")
    observation = build_news_sentiment_observation(articles, "2026-01-15", timestamp="2026-01-15T16:00:00Z", lookback_hours=1)
    assert observation["article_count"] == 0
    assert observation["sentiment_regime_label"] == "INSUFFICIENT_DATA"
