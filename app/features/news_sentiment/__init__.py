"""Dry-run news sentiment feature slice."""

from .news_sentiment_builder import build_news_sentiment_observation
from .news_sentiment_engine import (
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
from .news_sentiment_job import NewsSentimentDryRunResult, run_news_sentiment_dry_run
from .news_sentiment_report import build_news_sentiment_report
from .news_sentiment_validator import (
    NewsSentimentValidationError,
    NewsSentimentValidationResult,
    validate_news_sentiment_observation,
    validate_news_sentiment_observations,
)
from .news_sentiment_writer import NewsSentimentMockWriter, NewsSentimentWriterResult, write_news_sentiment_payloads

__all__ = [
    "NewsSentimentDryRunResult",
    "NewsSentimentMockWriter",
    "NewsSentimentValidationError",
    "NewsSentimentValidationResult",
    "NewsSentimentWriterResult",
    "build_news_sentiment_observation",
    "build_news_sentiment_report",
    "calculate_average_score",
    "calculate_narrative_pressure_score",
    "calculate_weighted_sentiment_score",
    "classify_sentiment_bucket",
    "count_articles_by_category",
    "count_articles_by_sentiment",
    "count_high_impact_articles",
    "determine_sentiment_regime_label",
    "filter_articles_by_lookback",
    "get_top_symbols_by_relevance",
    "normalize_news_category",
    "run_news_sentiment_dry_run",
    "validate_news_sentiment_observation",
    "validate_news_sentiment_observations",
    "write_news_sentiment_payloads",
]
