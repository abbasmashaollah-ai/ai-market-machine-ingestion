from copy import deepcopy

from app.features.news_sentiment.news_sentiment_builder import build_news_sentiment_observation
from app.features.news_sentiment.news_sentiment_writer import NewsSentimentMockWriter, write_news_sentiment_payloads
from tests.fixtures.news_sentiment_articles import build_news_sentiment_articles_scenario


def test_mock_writer_accepts_valid_rows() -> None:
    observation = build_news_sentiment_observation(build_news_sentiment_articles_scenario("positive_macro"), "2026-01-15")
    writer = NewsSentimentMockWriter()
    result = write_news_sentiment_payloads([observation], writer=writer)
    assert result.accepted_count == 1
    assert result.rejected_count == 0
    assert result.no_db_writes is True
    assert result.no_vendor_calls is True
    assert result.no_scheduler_activation is True
    assert writer.rows[0]["observation_date"] == "2026-01-15"


def test_mock_writer_rejects_invalid_rows_and_preserves_inputs() -> None:
    observation = build_news_sentiment_observation(build_news_sentiment_articles_scenario("positive_macro"), "2026-01-15")
    invalid = dict(observation)
    invalid["sentiment_regime_label"] = None
    snapshot = deepcopy(invalid)
    writer = NewsSentimentMockWriter()
    result = write_news_sentiment_payloads([invalid], writer=writer)
    assert result.accepted_count == 0
    assert result.rejected_count == 1
    assert invalid == snapshot
