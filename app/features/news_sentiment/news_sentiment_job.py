"""Dry-run orchestration for news sentiment observations."""

from __future__ import annotations

from dataclasses import dataclass

from .news_sentiment_builder import build_news_sentiment_observation
from .news_sentiment_report import build_news_sentiment_report
from .news_sentiment_validator import validate_news_sentiment_observation
from .news_sentiment_writer import NewsSentimentMockWriter, write_news_sentiment_payloads


@dataclass(frozen=True, slots=True)
class NewsSentimentDryRunResult:
    observation_rows: tuple[dict[str, object], ...]
    reports: tuple[dict[str, object], ...]
    writer_result: object
    accepted_count: int
    rejected_count: int
    warnings: tuple[str, ...]
    no_db_writes: bool = True
    no_vendor_calls: bool = True
    no_scheduler_activation: bool = True


def run_news_sentiment_dry_run(articles, observation_date, timestamp=None, lookback_hours=24, writer=None):
    observation = build_news_sentiment_observation(
        articles,
        observation_date,
        timestamp=timestamp,
        lookback_hours=lookback_hours,
    )
    validation = validate_news_sentiment_observation(observation)
    if not validation.is_valid:
        writer_result = write_news_sentiment_payloads([], writer=writer or NewsSentimentMockWriter())
        return NewsSentimentDryRunResult(
            observation_rows=(observation,),
            reports=(build_news_sentiment_report(observation, writer_result=writer_result),),
            writer_result=writer_result,
            accepted_count=0,
            rejected_count=1,
            warnings=tuple(str(error.message) for error in validation.errors),
        )

    writer_result = write_news_sentiment_payloads([observation], writer=writer)
    report = build_news_sentiment_report(observation, writer_result=writer_result)
    return NewsSentimentDryRunResult(
        observation_rows=(observation,),
        reports=(report,),
        writer_result=writer_result,
        accepted_count=writer_result.accepted_count,
        rejected_count=writer_result.rejected_count,
        warnings=tuple(),
    )
