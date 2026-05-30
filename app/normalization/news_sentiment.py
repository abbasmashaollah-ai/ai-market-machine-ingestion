from __future__ import annotations

from dataclasses import dataclass

from app.normalization.common import safe_number, safe_text


@dataclass(frozen=True)
class NormalizedNewsSentimentRecord:
    news_id: str | None
    published_at: str | None
    source: str | None
    publisher: str | None
    title: str | None
    summary: str | None
    url: str | None
    tickers: tuple[str, ...] | None
    sentiment_label: str | None
    sentiment_score: float | None
    raw_source_id: str | None
    notes: str | None


DEFAULT_FIXTURE_RECORDS: tuple[dict[str, object], ...] = (
    {
        "news_id": "news-aapl-2026-05-30-01",
        "published_at": "2026-05-30T14:30:00Z",
        "source": "manual_fixture",
        "publisher": "Fixture Newswire",
        "title": "Apple expands services coverage",
        "summary": "Deterministic fixture headline for AAPL news planning.",
        "url": "https://example.com/news/aapl-1",
        "tickers": ("AAPL",),
        "sentiment_label": "positive",
        "sentiment_score": 0.72,
        "raw_source_id": "fixture-aapl-1",
        "notes": "deterministic fixture",
    },
    {
        "news_id": "news-msft-2026-05-30-01",
        "published_at": "2026-05-30T15:00:00Z",
        "source": "manual_fixture",
        "publisher": "Fixture Newswire",
        "title": "Microsoft cloud segment remains in focus",
        "summary": "Deterministic fixture headline for MSFT news planning.",
        "url": "https://example.com/news/msft-1",
        "tickers": ("MSFT",),
        "sentiment_label": "neutral",
        "sentiment_score": 0.05,
        "raw_source_id": "fixture-msft-1",
        "notes": "deterministic fixture",
    },
    {
        "news_id": "news-nvda-2026-05-30-01",
        "published_at": "2026-05-30T15:30:00Z",
        "source": "manual_fixture",
        "publisher": "Fixture Newswire",
        "title": "Nvidia demand outlook appears strong",
        "summary": "Deterministic fixture headline for NVDA news planning.",
        "url": "https://example.com/news/nvda-1",
        "tickers": ("NVDA",),
        "sentiment_label": "positive",
        "sentiment_score": 0.81,
        "raw_source_id": "fixture-nvda-1",
        "notes": "deterministic fixture",
    },
)


def normalize_news_sentiment_record(payload: dict[str, object]) -> NormalizedNewsSentimentRecord:
    tickers = payload.get("tickers")
    normalized_tickers: tuple[str, ...] | None
    if isinstance(tickers, (list, tuple)):
        normalized_tickers = tuple(safe_text(ticker) for ticker in tickers if safe_text(ticker))
    else:
        normalized_tickers = None
    return NormalizedNewsSentimentRecord(
        news_id=safe_text(payload.get("news_id")),
        published_at=safe_text(payload.get("published_at")),
        source=safe_text(payload.get("source")),
        publisher=safe_text(payload.get("publisher")),
        title=safe_text(payload.get("title")),
        summary=safe_text(payload.get("summary")),
        url=safe_text(payload.get("url")),
        tickers=normalized_tickers,
        sentiment_label=safe_text(payload.get("sentiment_label")),
        sentiment_score=safe_number(payload.get("sentiment_score")),
        raw_source_id=safe_text(payload.get("raw_source_id")),
        notes=safe_text(payload.get("notes")),
    )


def validate_news_sentiment_record(record: NormalizedNewsSentimentRecord) -> tuple[str, ...]:
    errors: list[str] = []
    if not record.news_id:
        errors.append("news_id is required")
    if not record.published_at:
        errors.append("published_at is required")
    if not record.source:
        errors.append("source is required")
    if not record.publisher:
        errors.append("publisher is required")
    if not record.title:
        errors.append("title is required")
    if not record.summary:
        errors.append("summary is required")
    if not record.url:
        errors.append("url is required")
    if not record.tickers:
        errors.append("tickers is required")
    if record.sentiment_label is None and record.sentiment_score is None:
        errors.append("sentiment_label or sentiment_score is required")
    if not record.raw_source_id:
        errors.append("raw_source_id is required")
    if not record.notes:
        errors.append("notes is required")
    return tuple(errors)
