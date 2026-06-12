from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import urlparse

_STRATEGY_FIELDS = {
    "buy_signal",
    "sell_signal",
    "bullish",
    "bearish",
    "regime_impact",
    "risk_posture",
    "portfolio_action",
}

_SECRET_HINTS = (
    "apikey",
    "api_key",
    "token",
    "secret",
    "password",
    "passwd",
    "bearer ",
    "x-api-key",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_text(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    text = value.strip()
    return text or None


def _json_safe(value: Any) -> bool:
    try:
        json.dumps(value)
    except (TypeError, ValueError):
        return False
    return True


def _looks_secretish(value: str) -> bool:
    lower = value.lower()
    return any(hint in lower for hint in _SECRET_HINTS)


def _path_is_safe(path_value: str | None) -> bool:
    if path_value is None:
        return True
    text = path_value.strip()
    if not text:
        return False
    if _looks_secretish(text):
        return False
    parsed = urlparse(text)
    if parsed.scheme and parsed.scheme not in {"file"}:
        return False
    return True


def _url_is_safe(url_value: str | None) -> bool:
    if url_value is None:
        return True
    text = url_value.strip()
    if not text:
        return False
    if _looks_secretish(text):
        return False
    parsed = urlparse(text)
    if parsed.scheme and parsed.scheme not in {"http", "https"}:
        return False
    return True


def _parse_timestamp(value: Any) -> tuple[datetime | None, str | None]:
    text = _safe_text(value)
    if text is None:
        return None, "timestamp is required"
    try:
        candidate = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None, f"invalid timestamp: {text}"
    if candidate.tzinfo is None:
        candidate = candidate.replace(tzinfo=timezone.utc)
    return candidate.astimezone(timezone.utc), None


def _jsonl_safe_copy(record: Mapping[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(dict(record), ensure_ascii=False, sort_keys=True))


def _hash_idempotency_key(*parts: str | None) -> str:
    digest = hashlib.sha256()
    for part in parts:
        digest.update((part or "").encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def _canonicalize_z_timestamp(value: Any) -> Any:
    if isinstance(value, str) and value.endswith("+00:00"):
        return value[:-6] + "Z"
    return value


@dataclass(frozen=True, slots=True)
class NewsSentimentBatchMetadata:
    producer_run_id: str
    source_dataset: str
    vendor: str
    generated_at: str
    schema_version: str
    record_count: int
    source_sha256: str | None = None
    batch_sha256: str | None = None


@dataclass(frozen=True, slots=True)
class NewsSentimentRecord:
    news_id: str | None
    vendor_article_id: str | None
    vendor: str | None
    source_dataset: str | None
    source_name: str | None
    source_domain: str | None
    headline: str | None
    published_at: str | None
    collected_at: str | None
    producer_run_id: str | None
    url: str | None = None
    canonical_url: str | None = None
    summary: str | None = None
    content_snippet: str | None = None
    language: str | None = None
    author: str | None = None
    image_url: str | None = None
    updated_at: str | None = None
    tickers: tuple[str, ...] | None = None
    entities: tuple[Any, ...] | None = None
    topics: tuple[str, ...] | None = None
    countries: tuple[str, ...] | None = None
    asset_classes: tuple[str, ...] | None = None
    relevance_score: float | None = None
    raw_sentiment_score: float | None = None
    raw_sentiment_label: str | None = None
    sentiment_source: str | None = None
    source_sha256: str | None = None
    source_file_name: str | None = None
    source_file_path: str | None = None
    lineage: tuple[Any, ...] | None = None
    warnings: tuple[str, ...] | None = None


@dataclass(frozen=True, slots=True)
class NewsSentimentHandoffRecordResult:
    accepted: bool
    record: dict[str, Any] | None
    rejection_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    idempotency_key: str | None
    idempotency_components: dict[str, str] | None


@dataclass(frozen=True, slots=True)
class NewsSentimentHandoffWriteResult:
    records_received: int
    records_written: int
    records_rejected: int
    rejection_reasons: tuple[dict[str, Any], ...]
    output_path: str
    producer_run_id: str
    source_dataset: str
    vendor: str
    schema_version: str
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class NewsSentimentHandoffReadResult:
    records_read: int
    records: tuple[dict[str, Any], ...]
    malformed_lines: tuple[dict[str, Any], ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class NewsSentimentQuarantineResult:
    quarantine_path: str | None
    rejected_records: tuple[dict[str, Any], ...]
    written: bool


DEFAULT_FIXTURE_BATCH_METADATA = NewsSentimentBatchMetadata(
    producer_run_id="news-sentiment-fixture-run-001",
    source_dataset="news_sentiment_articles",
    vendor="fixture_vendor",
    generated_at="2026-05-30T16:00:00Z",
    schema_version="news_sentiment_jsonl_v1",
    record_count=3,
    source_sha256="fixture-source-sha256",
)

DEFAULT_FIXTURE_RECORDS: tuple[dict[str, Any], ...] = (
    {
        "news_id": "news-fixture-aapl-001",
        "vendor_article_id": "fixture-aapl-001",
        "vendor": "fixture_vendor",
        "source_dataset": "news_sentiment_articles",
        "source_name": "Fixture Newswire",
        "source_domain": "example.com",
        "headline": "Apple expands services coverage",
        "published_at": "2026-05-30T14:30:00Z",
        "collected_at": "2026-05-30T14:35:00Z",
        "producer_run_id": "news-sentiment-fixture-run-001",
        "url": "https://example.com/news/aapl-1",
        "canonical_url": "https://example.com/news/aapl-1",
        "summary": "Deterministic fixture article for AAPL.",
        "content_snippet": "Apple expands services coverage...",
        "language": "en",
        "author": "Fixture Reporter",
        "image_url": "https://example.com/images/aapl.png",
        "updated_at": "2026-05-30T14:36:00Z",
        "tickers": ["AAPL"],
        "entities": [{"type": "company", "name": "Apple"}],
        "topics": ["services"],
        "countries": ["US"],
        "asset_classes": ["equity"],
        "relevance_score": 0.92,
        "raw_sentiment_score": 0.7,
        "raw_sentiment_label": "positive",
        "sentiment_source": "vendor",
        "source_sha256": "fixture-record-sha256-aapl",
        "source_file_name": "fixture_aapl.jsonl",
        "source_file_path": "fixtures/news/fixture_aapl.jsonl",
        "lineage": ["fixture", "news"],
        "warnings": ["fixture-only"],
    },
    {
        "news_id": "news-fixture-msft-001",
        "vendor_article_id": "fixture-msft-001",
        "vendor": "fixture_vendor",
        "source_dataset": "news_sentiment_articles",
        "source_name": "Fixture Newswire",
        "source_domain": "example.com",
        "headline": "Microsoft cloud segment remains in focus",
        "published_at": "2026-05-30T15:00:00Z",
        "collected_at": "2026-05-30T15:05:00Z",
        "producer_run_id": "news-sentiment-fixture-run-001",
        "url": "https://example.com/news/msft-1",
        "canonical_url": "https://example.com/news/msft-1",
        "summary": "Deterministic fixture article for MSFT.",
        "tickers": ["MSFT"],
        "entities": [{"type": "company", "name": "Microsoft"}],
        "topics": ["cloud"],
        "countries": ["US"],
        "asset_classes": ["equity"],
        "relevance_score": 0.86,
        "raw_sentiment_score": 0.1,
        "raw_sentiment_label": "neutral",
        "sentiment_source": "vendor",
        "source_sha256": "fixture-record-sha256-msft",
        "source_file_name": "fixture_msft.jsonl",
        "source_file_path": "fixtures/news/fixture_msft.jsonl",
        "lineage": ["fixture", "news"],
        "warnings": ["fixture-only"],
    },
    {
        "news_id": "news-fixture-nvda-001",
        "vendor_article_id": "fixture-nvda-001",
        "vendor": "fixture_vendor",
        "source_dataset": "news_sentiment_articles",
        "source_name": "Fixture Newswire",
        "source_domain": "example.com",
        "headline": "Nvidia demand outlook appears strong",
        "published_at": "2026-05-30T15:30:00Z",
        "collected_at": "2026-05-30T15:35:00Z",
        "producer_run_id": "news-sentiment-fixture-run-001",
        "url": "https://example.com/news/nvda-1",
        "canonical_url": "https://example.com/news/nvda-1",
        "summary": "Deterministic fixture article for NVDA.",
        "tickers": ["NVDA"],
        "entities": [{"type": "company", "name": "Nvidia"}],
        "topics": ["demand"],
        "countries": ["US"],
        "asset_classes": ["equity"],
        "relevance_score": 0.81,
        "raw_sentiment_score": 0.8,
        "raw_sentiment_label": "positive",
        "sentiment_source": "vendor",
        "source_sha256": "fixture-record-sha256-nvda",
        "source_file_name": "fixture_nvda.jsonl",
        "source_file_path": "fixtures/news/fixture_nvda.jsonl",
        "lineage": ["fixture", "news"],
        "warnings": ["fixture-only"],
    },
)


def validate_news_sentiment_record(record: Mapping[str, Any]) -> NewsSentimentHandoffRecordResult:
    payload = dict(record)
    warnings: list[str] = []
    rejection_reasons: list[str] = []

    if payload.keys() & _STRATEGY_FIELDS:
        rejection_reasons.append("strategy fields are not allowed in ingestion handoff")

    news_id = _safe_text(payload.get("news_id"))
    vendor_article_id = _safe_text(payload.get("vendor_article_id"))
    vendor = _safe_text(payload.get("vendor"))
    source_dataset = _safe_text(payload.get("source_dataset"))
    source_name = _safe_text(payload.get("source_name"))
    source_domain = _safe_text(payload.get("source_domain"))
    headline = _safe_text(payload.get("headline"))
    url = _safe_text(payload.get("url"))
    canonical_url = _safe_text(payload.get("canonical_url"))
    summary = _safe_text(payload.get("summary"))
    content_snippet = _safe_text(payload.get("content_snippet"))
    language = _safe_text(payload.get("language"))
    author = _safe_text(payload.get("author"))
    image_url = _safe_text(payload.get("image_url"))
    updated_at = _safe_text(payload.get("updated_at"))
    producer_run_id = _safe_text(payload.get("producer_run_id"))
    raw_sentiment_label = _safe_text(payload.get("raw_sentiment_label"))
    sentiment_source = _safe_text(payload.get("sentiment_source"))
    source_sha256 = _safe_text(payload.get("source_sha256"))
    source_file_name = _safe_text(payload.get("source_file_name"))
    source_file_path = _safe_text(payload.get("source_file_path"))

    published_at, published_error = _parse_timestamp(payload.get("published_at"))
    collected_at, collected_error = _parse_timestamp(payload.get("collected_at"))
    if published_error:
        rejection_reasons.append("missing or invalid published_at")
    if collected_error:
        rejection_reasons.append("missing or invalid collected_at")

    if not headline:
        rejection_reasons.append("headline is required")
    if not vendor:
        rejection_reasons.append("vendor is required")
    if not source_dataset:
        rejection_reasons.append("source_dataset is required")
    if not source_name:
        rejection_reasons.append("source_name is required")
    if not source_domain:
        rejection_reasons.append("source_domain is required")
    if not producer_run_id:
        rejection_reasons.append("producer_run_id is required")
    if not (vendor_article_id or url or canonical_url or news_id):
        rejection_reasons.append("one of vendor_article_id, url, canonical_url, or news_id is required")
    if url and not _url_is_safe(url):
        rejection_reasons.append(
            "possible secret or credential detected in url" if _looks_secretish(url) else "unsafe url"
        )
    if canonical_url and not _url_is_safe(canonical_url):
        rejection_reasons.append(
            "possible secret or credential detected in canonical_url" if _looks_secretish(canonical_url) else "unsafe canonical_url"
        )
    if source_file_path and not _path_is_safe(source_file_path):
        rejection_reasons.append("unsafe source_file_path")
        rejection_reasons.append(
            "possible secret or credential detected in source_file_path"
            if _looks_secretish(source_file_path)
            else "unsafe source_file_path"
        )
    for text_value, label in (
        (headline, "headline"),
        (summary, "summary"),
        (content_snippet, "content_snippet"),
        (language, "language"),
        (author, "author"),
        (image_url, "image_url"),
        (updated_at, "updated_at"),
        (source_name, "source_name"),
        (source_domain, "source_domain"),
        (raw_sentiment_label, "raw_sentiment_label"),
        (sentiment_source, "sentiment_source"),
        (source_sha256, "source_sha256"),
        (source_file_name, "source_file_name"),
    ):
        if text_value is not None and _looks_secretish(text_value):
            rejection_reasons.append(f"possible secret or credential detected in {label}")

    tickers = payload.get("tickers")
    entities = payload.get("entities")
    topics = payload.get("topics")
    countries = payload.get("countries")
    asset_classes = payload.get("asset_classes")
    lineage = payload.get("lineage")
    warnings_field = payload.get("warnings")
    for label, value in (
        ("tickers", tickers),
        ("entities", entities),
        ("topics", topics),
        ("countries", countries),
        ("asset_classes", asset_classes),
        ("lineage", lineage),
        ("warnings", warnings_field),
    ):
        if value is not None and not _json_safe(value):
            rejection_reasons.append(f"{label} is not JSON-compatible")

    relevance_score = payload.get("relevance_score")
    if relevance_score is not None:
        try:
            relevance_value = float(relevance_score)
        except (TypeError, ValueError):
            rejection_reasons.append("relevance_score must be numeric when provided")
        else:
            if not 0.0 <= relevance_value <= 1.0:
                rejection_reasons.append("relevance_score must be between 0 and 1 when provided")
    raw_sentiment_score = payload.get("raw_sentiment_score")
    if raw_sentiment_score is not None:
        try:
            raw_sentiment_value = float(raw_sentiment_score)
        except (TypeError, ValueError):
            rejection_reasons.append("raw_sentiment_score must be numeric when provided")
        else:
            if not -1.0 <= raw_sentiment_value <= 1.0:
                rejection_reasons.append("raw_sentiment_score must be between -1 and 1 when provided")

    if raw_sentiment_label is not None and not raw_sentiment_label:
        rejection_reasons.append("raw_sentiment_label cannot be blank when provided")
    if published_at and collected_at and collected_at < published_at:
        warnings.append("collected_at is earlier than published_at")

    if rejection_reasons:
        return NewsSentimentHandoffRecordResult(
            accepted=False,
            record=None,
            rejection_reasons=tuple(dict.fromkeys(rejection_reasons)),
            warnings=tuple(warnings),
            idempotency_key=None,
            idempotency_components=None,
        )

    tickers_tuple = tuple(str(item).strip() for item in tickers) if isinstance(tickers, (list, tuple)) else None
    entities_tuple = tuple(entities) if isinstance(entities, (list, tuple)) else None
    topics_tuple = tuple(str(item).strip() for item in topics) if isinstance(topics, (list, tuple)) else None
    countries_tuple = tuple(str(item).strip() for item in countries) if isinstance(countries, (list, tuple)) else None
    asset_classes_tuple = tuple(str(item).strip() for item in asset_classes) if isinstance(asset_classes, (list, tuple)) else None
    lineage_tuple = tuple(lineage) if isinstance(lineage, (list, tuple)) else None
    warnings_tuple = tuple(str(item).strip() for item in warnings_field) if isinstance(warnings_field, (list, tuple)) else tuple(warnings)

    idempotency_components: dict[str, str] = {
        "vendor": vendor or "",
        "source_dataset": source_dataset or "",
        "vendor_article_id": vendor_article_id or "",
        "canonical_or_url": canonical_url or url or "",
        "published_at": published_at.isoformat() if published_at else "",
    }
    idempotency_key = _hash_idempotency_key(
        vendor or "",
        source_dataset or "",
        vendor_article_id or "",
        canonical_url or url or "",
        published_at.isoformat() if published_at else "",
    )
    normalized = {
        "news_id": news_id,
        "vendor_article_id": vendor_article_id,
        "vendor": vendor,
        "source_dataset": source_dataset,
        "source_name": source_name,
        "source_domain": source_domain,
        "headline": headline,
        "published_at": published_at.isoformat() if published_at else None,
        "collected_at": collected_at.isoformat() if collected_at else None,
        "producer_run_id": producer_run_id,
        "url": url,
        "canonical_url": canonical_url,
        "summary": summary,
        "content_snippet": content_snippet,
        "language": language,
        "author": author,
        "image_url": image_url,
        "updated_at": updated_at,
        "tickers": tickers_tuple,
        "entities": entities_tuple,
        "topics": topics_tuple,
        "countries": countries_tuple,
        "asset_classes": asset_classes_tuple,
        "relevance_score": float(relevance_score) if relevance_score is not None else None,
        "raw_sentiment_score": float(raw_sentiment_score) if raw_sentiment_score is not None else None,
        "raw_sentiment_label": raw_sentiment_label,
        "sentiment_source": sentiment_source,
        "source_sha256": source_sha256,
        "source_file_name": source_file_name,
        "source_file_path": source_file_path,
        "lineage": lineage_tuple,
        "warnings": warnings_tuple,
    }
    return NewsSentimentHandoffRecordResult(
        accepted=True,
        record=normalized,
        rejection_reasons=tuple(),
        warnings=tuple(warnings),
        idempotency_key=idempotency_key,
        idempotency_components=idempotency_components,
    )


def write_news_sentiment_handoff_jsonl(
    records: Sequence[Mapping[str, Any]],
    output_path: str | Path,
    *,
    batch_metadata: NewsSentimentBatchMetadata,
    quarantine_path: str | Path | None = None,
) -> NewsSentimentHandoffWriteResult:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    quarantine_target = Path(quarantine_path) if quarantine_path is not None else None
    if quarantine_target is not None:
        quarantine_target.parent.mkdir(parents=True, exist_ok=True)

    written_records: list[dict[str, Any]] = []
    rejection_reasons: list[dict[str, Any]] = []
    quarantined_records: list[dict[str, Any]] = []

    for index, record in enumerate(records):
        result = validate_news_sentiment_record(record)
        if not result.accepted or result.record is None:
            rejected = {
                "index": index,
                "rejection_reasons": list(result.rejection_reasons),
                "warnings": list(result.warnings),
                "record": _jsonl_safe_copy(record),
            }
            rejection_reasons.append(rejected)
            quarantined_records.append(rejected)
            continue
        enriched = dict(result.record)
        for field_name in ("published_at", "collected_at", "updated_at"):
            enriched[field_name] = _canonicalize_z_timestamp(enriched.get(field_name))
        enriched.setdefault("producer_run_id", batch_metadata.producer_run_id)
        enriched.setdefault("source_dataset", batch_metadata.source_dataset)
        enriched.setdefault("vendor", batch_metadata.vendor)
        enriched.setdefault("generated_at", batch_metadata.generated_at)
        enriched.setdefault("schema_version", batch_metadata.schema_version)
        enriched.setdefault("record_count", batch_metadata.record_count)
        enriched.setdefault("source_sha256", batch_metadata.source_sha256)
        enriched.setdefault("batch_sha256", batch_metadata.batch_sha256)
        enriched.setdefault("idempotency_key", result.idempotency_key)
        enriched.setdefault("idempotency_components", result.idempotency_components)
        written_records.append(enriched)

    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in written_records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")

    quarantine_written = False
    if quarantine_target is not None and quarantined_records:
        quarantine_written = True
        with quarantine_target.open("w", encoding="utf-8", newline="\n") as handle:
            for record in quarantined_records:
                handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
                handle.write("\n")

    return NewsSentimentHandoffWriteResult(
        records_received=len(records),
        records_written=len(written_records),
        records_rejected=len(rejection_reasons),
        rejection_reasons=tuple(rejection_reasons),
        output_path=str(output_path),
        producer_run_id=batch_metadata.producer_run_id,
        source_dataset=batch_metadata.source_dataset,
        vendor=batch_metadata.vendor,
        schema_version=batch_metadata.schema_version,
        warnings=tuple(),
    )


def read_news_sentiment_handoff_jsonl(path: str | Path) -> NewsSentimentHandoffReadResult:
    path = Path(path)
    records: list[dict[str, Any]] = []
    malformed_lines: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                record = json.loads(text)
            except json.JSONDecodeError as exc:
                malformed_lines.append({"line_number": line_number, "error": exc.msg})
                continue
            if not isinstance(record, dict):
                malformed_lines.append({"line_number": line_number, "error": "expected JSON object"})
                continue
            records.append(record)
    return NewsSentimentHandoffReadResult(
        records_read=len(records),
        records=tuple(records),
        malformed_lines=tuple(malformed_lines),
        warnings=tuple(),
    )


def _fixture_summary(*, output_file: Path | None = None, summary_only: bool = False) -> dict[str, Any]:
    batch_metadata = DEFAULT_FIXTURE_BATCH_METADATA
    output_path = output_file or Path("outputs") / "handoff" / "news_sentiment" / "news_sentiment_fixture.jsonl"
    result = write_news_sentiment_handoff_jsonl(DEFAULT_FIXTURE_RECORDS, output_path, batch_metadata=batch_metadata)
    read_result = read_news_sentiment_handoff_jsonl(output_path)
    payload = {
        "records_received": result.records_received,
        "records_written": result.records_written,
        "records_rejected": result.records_rejected,
        "producer_run_id": result.producer_run_id,
        "source_dataset": result.source_dataset,
        "vendor": result.vendor,
        "schema_version": result.schema_version,
        "records_read": read_result.records_read,
        "malformed_lines": list(read_result.malformed_lines),
        "no_vendor_calls": True,
        "no_db_writes": True,
        "no_ai_sentiment": True,
        "no_trading_signals": True,
        "no_regime_risk_portfolio_logic": True,
    }
    if not summary_only:
        payload["records"] = list(read_result.records)
        payload["rejections"] = list(result.rejection_reasons)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run the news/sentiment JSONL handoff locally.")
    parser.add_argument("--output-file", help="Optional local JSONL output file.")
    parser.add_argument("--summary-only", action="store_true", help="Print a compact JSON summary only.")
    args = parser.parse_args(argv)

    output_file = Path(args.output_file) if args.output_file else None
    payload = _fixture_summary(output_file=output_file, summary_only=bool(args.summary_only))
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
