import json

from app.features.news_sentiment.news_sentiment_builder import build_news_sentiment_observation
from app.features.news_sentiment.news_sentiment_report import build_news_sentiment_report
from tests.fixtures.news_sentiment_articles import build_news_sentiment_articles_scenario


def test_report_contains_required_fields() -> None:
    observation = build_news_sentiment_observation(build_news_sentiment_articles_scenario("high_impact_negative"), "2026-01-15")
    report = build_news_sentiment_report(observation, writer_result=type("R", (), {"accepted_count": 1, "rejected_count": 0})())
    assert report["sentiment_regime_label"]
    assert report["article_count"] == 3
    assert report["accepted_count"] == 1
    assert report["rejected_count"] == 0
    assert report["safety_flags"]["no_db_writes"] is True
    json.dumps(report)
