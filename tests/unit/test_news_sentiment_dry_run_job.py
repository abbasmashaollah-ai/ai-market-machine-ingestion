import json
from datetime import datetime, timezone

from app.features.news_sentiment.news_sentiment_job import run_news_sentiment_dry_run
from app.features.news_sentiment.news_sentiment_report import build_news_sentiment_report
from tests.fixtures.news_sentiment_articles import build_news_sentiment_articles_scenario


def test_dry_run_produces_report_and_safety_flags() -> None:
    articles = build_news_sentiment_articles_scenario("negative_macro")
    result = run_news_sentiment_dry_run(articles, "2026-01-15", timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc))
    assert result.accepted_count == 1
    assert result.rejected_count == 0
    assert result.reports
    report = result.reports[0]
    assert report["sentiment_regime_label"]
    assert report["safety_flags"]["no_db_writes"] is True
    assert report["safety_flags"]["no_vendor_calls"] is True
    assert report["safety_flags"]["no_scheduler_activation"] is True
    json.dumps(report)
    assert build_news_sentiment_report(result.observation_rows[0], writer_result=result.writer_result)["sentiment_regime_label"] == report["sentiment_regime_label"]
