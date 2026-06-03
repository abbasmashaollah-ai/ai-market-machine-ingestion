"""Validation helpers for news sentiment observations."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from .news_sentiment_engine import ALLOWED_SENTIMENT_LABELS


@dataclass(frozen=True, slots=True)
class NewsSentimentValidationError:
    field_name: str
    message: str


@dataclass(frozen=True, slots=True)
class NewsSentimentValidationResult:
    is_valid: bool
    errors: tuple[NewsSentimentValidationError, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


def _is_positive_int(value: object) -> bool:
    return isinstance(value, int) and value > 0 and not isinstance(value, bool)


def _is_non_negative_int(value: object) -> bool:
    return isinstance(value, int) and value >= 0 and not isinstance(value, bool)


def _is_numeric_or_none(value: object) -> bool:
    return value is None or isinstance(value, (int, float)) and not isinstance(value, bool)


def _non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _label_from_section(section: Mapping[str, object], key: str) -> str | None:
    value = section.get(key)
    if isinstance(value, str) and value.strip():
        return value
    report = section.get("report")
    if isinstance(report, Mapping):
        value = report.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return None


def validate_news_sentiment_observation(row):
    errors: list[NewsSentimentValidationError] = []
    if not isinstance(row, Mapping):
        return NewsSentimentValidationResult(False, (NewsSentimentValidationError("row", "row must be a mapping"),), ())

    required_fields = ("observation_date", "source", "lookback_hours", "articles", "article_count", "sentiment_regime_label")
    for field_name in required_fields:
        if field_name not in row:
            errors.append(NewsSentimentValidationError(field_name, "field is required"))

    if not _non_empty_string(row.get("observation_date")):
        errors.append(NewsSentimentValidationError("observation_date", "observation_date must be a non-empty string"))
    if not _non_empty_string(row.get("source")):
        errors.append(NewsSentimentValidationError("source", "source must be a non-empty string"))
    if not _is_positive_int(row.get("lookback_hours")):
        errors.append(NewsSentimentValidationError("lookback_hours", "lookback_hours must be a positive integer"))
    if not isinstance(row.get("articles"), list):
        errors.append(NewsSentimentValidationError("articles", "articles must be a list"))
    if not _is_non_negative_int(row.get("article_count")):
        errors.append(NewsSentimentValidationError("article_count", "article_count must be a non-negative integer"))

    for field_name in (
        "positive_article_count",
        "negative_article_count",
        "neutral_article_count",
        "high_impact_article_count",
        "macro_article_count",
        "earnings_article_count",
        "fed_article_count",
        "geopolitical_article_count",
        "sector_article_count",
        "company_article_count",
    ):
        if field_name in row and not _is_non_negative_int(row.get(field_name)):
            errors.append(NewsSentimentValidationError(field_name, "field must be a non-negative integer when present"))

    for field_name in ("average_sentiment_score", "average_relevance_score", "average_impact_score", "weighted_sentiment_score", "narrative_pressure_score"):
        if field_name in row and not _is_numeric_or_none(row.get(field_name)):
            errors.append(NewsSentimentValidationError(field_name, "field must be numeric or None"))

    if "top_symbols" in row and not isinstance(row.get("top_symbols"), list):
        errors.append(NewsSentimentValidationError("top_symbols", "top_symbols must be a list when present"))

    label = row.get("sentiment_regime_label")
    if not _non_empty_string(label) or label not in ALLOWED_SENTIMENT_LABELS:
        errors.append(NewsSentimentValidationError("sentiment_regime_label", "sentiment_regime_label must be an allowed non-empty label"))

    return NewsSentimentValidationResult(is_valid=not errors, errors=tuple(errors), warnings=())


def validate_news_sentiment_observations(rows):
    errors: list[NewsSentimentValidationError] = []
    seen: set[tuple[str, str]] = set()
    for index, row in enumerate(rows or []):
        result = validate_news_sentiment_observation(row)
        errors.extend(result.errors)
        if isinstance(row, Mapping) and _non_empty_string(row.get("observation_date")) and _non_empty_string(row.get("source")):
            key = (str(row["observation_date"]), str(row["source"]))
            if key in seen:
                errors.append(NewsSentimentValidationError(f"rows[{index}]", "duplicate batch key observation_date + source"))
            seen.add(key)
    return NewsSentimentValidationResult(is_valid=not errors, errors=tuple(errors), warnings=())
