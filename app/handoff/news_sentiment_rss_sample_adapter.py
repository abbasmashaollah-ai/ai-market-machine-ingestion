from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from app.handoff.news_sentiment_fixture_normalizer import normalize_fixture_news_record
from app.handoff.news_sentiment_handoff import (
    NewsSentimentBatchMetadata,
    NewsSentimentHandoffRecordResult,
)


@dataclass(frozen=True, slots=True)
class NewsSentimentRssSampleNormalizationResult:
    normalized_records: tuple[dict[str, Any], ...]
    rejected_records: tuple[dict[str, Any], ...]
    warnings: tuple[str, ...]


def _safe_text(value: Any) -> str | None:
    if value is None or not isinstance(value, str):
        return None
    text = value.strip()
    return text or None


def _parse_timestamp(value: Any) -> str | None:
    text = _safe_text(value)
    if text is None:
        return None
    parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_list(value: Any) -> list[str] | None:
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        return [str(item).strip() for item in value if _safe_text(item)]
    return None


def _deterministic_news_id(*parts: str | None) -> str:
    digest = hashlib.sha256()
    for part in parts:
        digest.update((part or "").encode("utf-8"))
        digest.update(b"\0")
    return f"news-{digest.hexdigest()[:24]}"


def _is_secret_like(url: str | None) -> bool:
    if not url:
        return False
    lower = url.lower()
    return any(marker in lower for marker in ("token=", "api_key", "apikey", "secret", "password", "credential"))


def normalize_rss_sample_item(item: Mapping[str, Any], *, batch_metadata: NewsSentimentBatchMetadata) -> dict[str, Any]:
    title = _safe_text(item.get("title"))
    published = _parse_timestamp(item.get("published"))
    link = _safe_text(item.get("link"))
    if _is_secret_like(link):
        raise ValueError("secret-like link rejected")
    raw_record = {
        "news_id": _safe_text(item.get("news_id"))
        or _deterministic_news_id(batch_metadata.vendor, batch_metadata.source_dataset, _safe_text(item.get("guid")), title, published, link),
        "vendor_article_id": _safe_text(item.get("guid")) or _safe_text(item.get("article_id")),
        "source": _safe_text(item.get("source_name")) or _safe_text(item.get("source")) or "RSS Feed",
        "domain": _safe_text(item.get("source_domain")),
        "title": title,
        "published_at": published,
        "collected_at": _parse_timestamp(item.get("collected_at")) or batch_metadata.generated_at,
        "url": link,
        "summary": _safe_text(item.get("summary")),
        "symbols": _safe_list(item.get("symbols")) or _safe_list(item.get("tickers")),
        "topics": _safe_list(item.get("categories")) or _safe_list(item.get("topics")),
        "sentiment_score": item.get("sentiment_score"),
        "sentiment_label": _safe_text(item.get("sentiment_label")),
        "source_file_name": _safe_text(item.get("source_file_name")),
    }
    normalized = normalize_fixture_news_record(raw_record, batch_metadata=batch_metadata)
    normalized["vendor_article_id"] = raw_record["vendor_article_id"]
    normalized["source_name"] = raw_record["source"]
    normalized["source_domain"] = raw_record["domain"] or normalized.get("source_domain")
    normalized["canonical_url"] = link
    normalized["url"] = link
    return normalized


def normalize_rss_sample_items(
    items: Sequence[Mapping[str, Any]],
    *,
    batch_metadata: NewsSentimentBatchMetadata,
) -> NewsSentimentRssSampleNormalizationResult:
    normalized: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    warnings: list[str] = []
    for index, item in enumerate(items):
        try:
            normalized.append(normalize_rss_sample_item(item, batch_metadata=batch_metadata))
        except Exception as exc:  # pragma: no cover - in-memory quarantine path
            rejected.append({"index": index, "error": str(exc), "record": dict(item)})
            warnings.append(str(exc))
    return NewsSentimentRssSampleNormalizationResult(
        normalized_records=tuple(normalized),
        rejected_records=tuple(rejected),
        warnings=tuple(warnings),
    )


def load_rss_sample_items(path: str | Path) -> list[dict[str, Any]]:
    rss_path = Path(path)
    payload = json.loads(rss_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("rss sample file must contain a JSON list of objects")
    items: list[dict[str, Any]] = []
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError("rss sample items must be JSON objects")
        items.append(dict(item))
    return items

