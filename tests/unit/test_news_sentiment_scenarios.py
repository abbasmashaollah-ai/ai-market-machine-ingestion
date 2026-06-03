from app.features.news_sentiment.news_sentiment_builder import build_news_sentiment_observation
from tests.fixtures.news_sentiment_articles import build_news_sentiment_articles_scenario


def test_scenarios_produce_different_labels() -> None:
    labels = {
        scenario: build_news_sentiment_observation(build_news_sentiment_articles_scenario(scenario), "2026-01-15")["sentiment_regime_label"]
        for scenario in ("positive_macro", "negative_macro", "mixed_market", "high_impact_negative", "high_impact_positive", "low_signal")
    }
    assert labels["positive_macro"] in {"POSITIVE_SENTIMENT", "HIGH_IMPACT_POSITIVE"}
    assert labels["negative_macro"] in {"NEGATIVE_SENTIMENT", "HIGH_IMPACT_NEGATIVE"}
    assert labels["mixed_market"] in {"MIXED_SENTIMENT", "LOW_SIGNAL_SENTIMENT"}
    assert labels["high_impact_negative"] == "HIGH_IMPACT_NEGATIVE"
    assert labels["high_impact_positive"] == "HIGH_IMPACT_POSITIVE"
    assert labels["low_signal"] in {"LOW_SIGNAL_SENTIMENT", "INSUFFICIENT_DATA"}
