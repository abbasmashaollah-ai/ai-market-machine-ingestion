from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence
from urllib.parse import urlparse

from app.handoff.news_sentiment_handoff import (
    NewsSentimentBatchMetadata,
    NewsSentimentHandoffRecordResult,
    validate_news_sentiment_record,
)


@dataclass(frozen=True, slots=True)
class NewsSentimentFixtureNormalizationResult:
    normalized_records: tuple[dict[str, Any], ...]
    rejected_records: tuple[dict[str, Any], ...]
    warnings: tuple[str, ...]


def _safe_text(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    text = value.strip()
    return text or None


def _parse_timestamp(value: Any) -> str | None:
    text = _safe_text(value)
    if text is None:
        return None
    candidate = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if candidate.tzinfo is None:
        candidate = candidate.replace(tzinfo=timezone.utc)
    return candidate.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_list(value: Any) -> list[Any] | None:
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        return list(value)
    return None


def _deterministic_news_id(*parts: str | None) -> str:
    digest = hashlib.sha256()
    for part in parts:
        digest.update((part or "").encode("utf-8"))
        digest.update(b"\0")
    return f"news-{digest.hexdigest()[:24]}"


def _source_domain_from_url(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urlparse(url)
    return parsed.netloc or None


def normalize_fixture_news_record(
    raw_record: Mapping[str, Any],
    *,
    batch_metadata: NewsSentimentBatchMetadata,
) -> dict[str, Any]:
    source = _safe_text(raw_record.get("source"))
    title = _safe_text(raw_record.get("title"))
    summary = _safe_text(raw_record.get("summary"))
    url = _safe_text(raw_record.get("url"))
    article_id = _safe_text(raw_record.get("id")) or _safe_text(raw_record.get("article_id"))
    vendor_article_id = _safe_text(raw_record.get("vendor_article_id")) or article_id
    published_at = _parse_timestamp(raw_record.get("published_at"))
    collected_at = _parse_timestamp(raw_record.get("collected_at")) or batch_metadata.generated_at
    symbols = _safe_list(raw_record.get("symbols")) or _safe_list(raw_record.get("tickers"))
    topics = _safe_list(raw_record.get("topics"))
    sentiment_score = raw_record.get("sentiment_score")
    sentiment_label = _safe_text(raw_record.get("sentiment_label"))
    source_domain = _safe_text(raw_record.get("domain")) or _source_domain_from_url(url)

    news_id = _safe_text(raw_record.get("news_id")) or _deterministic_news_id(
        batch_metadata.vendor,
        batch_metadata.source_dataset,
        vendor_article_id,
        title,
        published_at,
        url,
    )

    published_at_value = published_at
    collected_at_value = collected_at
    updated_at_value = _parse_timestamp(raw_record.get("updated_at"))

    normalized = {
        "news_id": news_id,
        "vendor_article_id": vendor_article_id,
        "vendor": batch_metadata.vendor,
        "source_dataset": batch_metadata.source_dataset,
        "source_name": source,
        "source_domain": source_domain,
        "headline": title,
        "published_at": published_at_value,
        "collected_at": collected_at_value,
        "producer_run_id": batch_metadata.producer_run_id,
        "url": url,
        "canonical_url": url,
        "summary": summary,
        "content_snippet": summary,
        "language": _safe_text(raw_record.get("language")) or "en",
        "author": _safe_text(raw_record.get("author")),
        "image_url": _safe_text(raw_record.get("image_url")),
        "updated_at": updated_at_value,
        "tickers": tuple(str(item).strip() for item in symbols if _safe_text(item)) if symbols is not None else None,
        "entities": tuple({"type": "symbol", "value": item} for item in symbols if _safe_text(item)) if symbols is not None else None,
        "topics": tuple(str(item).strip() for item in topics if _safe_text(item)) if topics is not None else None,
        "countries": _safe_list(raw_record.get("countries")),
        "asset_classes": _safe_list(raw_record.get("asset_classes")),
        "relevance_score": float(raw_record["relevance_score"]) if raw_record.get("relevance_score") is not None else None,
        "raw_sentiment_score": float(sentiment_score) if sentiment_score is not None else None,
        "raw_sentiment_label": sentiment_label,
        "sentiment_source": "fixture_vendor",
        "source_sha256": _safe_text(raw_record.get("source_sha256")),
        "source_file_name": _safe_text(raw_record.get("source_file_name")),
        "source_file_path": None,
        "lineage": tuple(["fixture", batch_metadata.source_dataset]),
        "warnings": tuple(["fixture-normalized"]),
    }
    result = validate_news_sentiment_record(normalized)
    if not result.accepted or result.record is None:
        raise ValueError(f"fixture record failed handoff validation: {result.rejection_reasons}")
    normalized_record = dict(result.record)
    if isinstance(normalized_record.get("published_at"), str):
        normalized_record["published_at"] = normalized_record["published_at"].replace("+00:00", "Z")
    if isinstance(normalized_record.get("collected_at"), str):
        normalized_record["collected_at"] = normalized_record["collected_at"].replace("+00:00", "Z")
    if isinstance(normalized_record.get("updated_at"), str):
        normalized_record["updated_at"] = normalized_record["updated_at"].replace("+00:00", "Z")
    return normalized_record


def normalize_fixture_news_records(
    raw_records: Sequence[Mapping[str, Any]],
    *,
    batch_metadata: NewsSentimentBatchMetadata,
) -> NewsSentimentFixtureNormalizationResult:
    normalized: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    warnings: list[str] = []
    for index, record in enumerate(raw_records):
        try:
            normalized.append(normalize_fixture_news_record(record, batch_metadata=batch_metadata))
        except Exception as exc:  # pragma: no cover - simple fixture quarantine path
            rejected.append({"index": index, "error": str(exc), "record": dict(record)})
            warnings.append(str(exc))
    return NewsSentimentFixtureNormalizationResult(
        normalized_records=tuple(normalized),
        rejected_records=tuple(rejected),
        warnings=tuple(warnings),
    )


def load_fixture_news_records(path: str | Path) -> list[dict[str, Any]]:
    fixture_path = Path(path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("fixture file must contain a JSON list of records")
    records: list[dict[str, Any]] = []
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError("fixture file items must be JSON objects")
        records.append(dict(item))
    return records
