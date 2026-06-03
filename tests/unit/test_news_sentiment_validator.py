from copy import deepcopy

from app.features.news_sentiment.news_sentiment_builder import build_news_sentiment_observation
from app.features.news_sentiment.news_sentiment_validator import validate_news_sentiment_observation
from tests.fixtures.news_sentiment_articles import build_news_sentiment_articles_scenario


def test_valid_observation_passes() -> None:
    observation = build_news_sentiment_observation(build_news_sentiment_articles_scenario("positive_macro"), "2026-01-15")
    result = validate_news_sentiment_observation(observation)
    assert result.is_valid is True
    assert result.errors == ()


def test_invalid_rows_fail() -> None:
    observation = build_news_sentiment_observation(build_news_sentiment_articles_scenario("positive_macro"), "2026-01-15")
    invalid = dict(observation)
    invalid.pop("articles")
    invalid["lookback_hours"] = 0
    invalid["sentiment_regime_label"] = None
    result = validate_news_sentiment_observation(invalid)
    fields = {error.field_name for error in result.errors}
    assert "articles" in fields
    assert "lookback_hours" in fields
    assert "sentiment_regime_label" in fields


def test_validator_does_not_mutate_input() -> None:
    observation = build_news_sentiment_observation(build_news_sentiment_articles_scenario("positive_macro"), "2026-01-15")
    snapshot = deepcopy(observation)
    validate_news_sentiment_observation(observation)
    assert observation == snapshot
