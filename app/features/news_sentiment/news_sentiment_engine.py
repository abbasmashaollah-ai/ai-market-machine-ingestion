"""Pure evidence helpers for fixture-only news sentiment observations."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

ALLOWED_NEWS_CATEGORIES = {
    "MACRO",
    "EARNINGS",
    "FED",
    "GEOPOLITICAL",
    "SECTOR",
    "COMPANY",
    "CREDIT",
    "VOLATILITY",
    "OTHER",
}

ALLOWED_SENTIMENT_LABELS = {
    "POSITIVE_SENTIMENT",
    "NEGATIVE_SENTIMENT",
    "MIXED_SENTIMENT",
    "HIGH_IMPACT_NEGATIVE",
    "HIGH_IMPACT_POSITIVE",
    "LOW_SIGNAL_SENTIMENT",
    "INSUFFICIENT_DATA",
}


def _parse_datetime(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _to_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def normalize_news_category(category) -> str:
    normalized = str(category or "").strip().upper()
    return normalized if normalized in ALLOWED_NEWS_CATEGORIES else "OTHER"


def filter_articles_by_lookback(articles, observation_datetime, lookback_hours):
    if not isinstance(observation_datetime, datetime):
        return []
    if observation_datetime.tzinfo is None:
        observation_datetime = observation_datetime.replace(tzinfo=timezone.utc)
    window_start = observation_datetime.astimezone(timezone.utc) - timedelta(hours=int(lookback_hours))
    filtered = []
    for article in articles or []:
        published_at = _parse_datetime(article.get("published_at")) if isinstance(article, dict) else None
        if published_at is None:
            continue
        if window_start <= published_at <= observation_datetime.astimezone(timezone.utc):
            filtered.append(article)
    return filtered


def classify_sentiment_bucket(sentiment_score):
    score = _to_float(sentiment_score)
    if score is None:
        return "INSUFFICIENT_DATA"
    if score >= 0.2:
        return "POSITIVE"
    if score <= -0.2:
        return "NEGATIVE"
    return "NEUTRAL"


def count_articles_by_sentiment(articles):
    counts = Counter({"positive": 0, "negative": 0, "neutral": 0})
    for article in articles or []:
        bucket = classify_sentiment_bucket(article.get("sentiment_score") if isinstance(article, dict) else None)
        if bucket == "POSITIVE":
            counts["positive"] += 1
        elif bucket == "NEGATIVE":
            counts["negative"] += 1
        elif bucket == "NEUTRAL":
            counts["neutral"] += 1
    return dict(counts)


def count_articles_by_category(articles):
    counts = Counter()
    for article in articles or []:
        category = normalize_news_category(article.get("category") if isinstance(article, dict) else None)
        counts[category] += 1
    return dict(counts)


def count_high_impact_articles(articles, threshold=0.75):
    count = 0
    for article in articles or []:
        score = _to_float(article.get("impact_score") if isinstance(article, dict) else None)
        if score is not None and score >= float(threshold):
            count += 1
    return count


def calculate_average_score(articles, field):
    values = []
    for article in articles or []:
        if isinstance(article, dict):
            value = _to_float(article.get(field))
            if value is not None:
                values.append(value)
    if not values:
        return None
    return sum(values) / len(values)


def calculate_weighted_sentiment_score(articles):
    numerator = 0.0
    denominator = 0.0
    for article in articles or []:
        if not isinstance(article, dict):
            continue
        sentiment = _to_float(article.get("sentiment_score"))
        relevance = _to_float(article.get("relevance_score"))
        impact = _to_float(article.get("impact_score"))
        if sentiment is None or relevance is None or impact is None:
            continue
        weight = max(relevance, 0.0) * max(impact, 0.0)
        numerator += sentiment * weight
        denominator += weight
    if denominator == 0.0:
        return None
    return numerator / denominator


def calculate_narrative_pressure_score(articles):
    if not articles:
        return None
    weighted = calculate_weighted_sentiment_score(articles)
    average_relevance = calculate_average_score(articles, "relevance_score")
    average_impact = calculate_average_score(articles, "impact_score")
    if weighted is None or average_relevance is None or average_impact is None:
        return None
    pressure = abs(weighted) * (average_relevance + average_impact) / 2.0
    return max(0.0, min(1.0, pressure))


def get_top_symbols_by_relevance(articles, top_n=5):
    scores: dict[str, float] = defaultdict(float)
    first_seen: dict[str, int] = {}
    for article in articles or []:
        if not isinstance(article, dict):
            continue
        relevance = _to_float(article.get("relevance_score"))
        if relevance is None:
            continue
        symbols = article.get("symbols") or []
        for symbol in symbols:
            symbol_text = str(symbol or "").upper().strip()
            if symbol_text:
                scores[symbol_text] += relevance
                if symbol_text not in first_seen:
                    first_seen[symbol_text] = len(first_seen)
    ranked = sorted(scores.items(), key=lambda item: (-item[1], first_seen.get(item[0], 0)))
    return [symbol for symbol, _ in ranked[: int(top_n)]]


def determine_sentiment_regime_label(weighted_sentiment_score=None, high_impact_negative_count=None, high_impact_positive_count=None, article_count=None):
    if not article_count:
        return "INSUFFICIENT_DATA"
    weighted = _to_float(weighted_sentiment_score)
    negatives = int(high_impact_negative_count or 0)
    positives = int(high_impact_positive_count or 0)
    if weighted is None:
        return "LOW_SIGNAL_SENTIMENT" if article_count else "INSUFFICIENT_DATA"
    if negatives > positives and weighted <= -0.2:
        return "HIGH_IMPACT_NEGATIVE"
    if positives > negatives and weighted >= 0.2:
        return "HIGH_IMPACT_POSITIVE"
    if weighted >= 0.15:
        return "POSITIVE_SENTIMENT"
    if weighted <= -0.15:
        return "NEGATIVE_SENTIMENT"
    if abs(weighted) < 0.1 and article_count <= 2:
        return "LOW_SIGNAL_SENTIMENT"
    return "MIXED_SENTIMENT"
