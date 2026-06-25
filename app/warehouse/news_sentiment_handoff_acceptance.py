from __future__ import annotations

from dataclasses import dataclass, field
from json import JSONDecodeError, loads
from pathlib import Path
from typing import Any

from app.handoff.news_sentiment_handoff import NewsSentimentHandoffRecordResult, validate_news_sentiment_record, write_news_sentiment_handoff_jsonl


@dataclass(frozen=True, slots=True)
class NewsSentimentHandoffAcceptanceSummary:
    file_path: str
    lines_read: int
    records_parsed: int
    records_accepted: int
    records_written: int
    records_rejected: int
    malformed_lines: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    rejection_reasons: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


def _load_jsonl_lines(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    parsed: list[dict[str, Any]] = []
    malformed: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                payload = loads(text)
            except JSONDecodeError as exc:
                malformed.append({"line_number": line_number, "error": exc.msg})
                continue
            if not isinstance(payload, dict):
                malformed.append({"line_number": line_number, "error": "expected JSON object"})
                continue
            parsed.append(dict(payload))
    return parsed, malformed


def import_news_sentiment_handoff_jsonl(
    input_path: str | Path,
    *,
    output_path: str | Path | None = None,
    quarantine_path: str | Path | None = None,
) -> NewsSentimentHandoffAcceptanceSummary:
    path = Path(input_path)
    records, malformed_lines = _load_jsonl_lines(path)
    validation_results: list[NewsSentimentHandoffRecordResult] = [validate_news_sentiment_record(record) for record in records]

    accepted_records: list[dict[str, Any]] = []
    rejection_reasons: list[str] = []
    warnings: list[str] = []
    for validation in validation_results:
        warnings.extend(validation.warnings)
        if validation.accepted and validation.record is not None:
            accepted_records.append(validation.record)
        else:
            rejection_reasons.extend(validation.rejection_reasons)

    records_written = 0
    if output_path is not None and accepted_records:
        from app.handoff.news_sentiment_handoff import DEFAULT_FIXTURE_BATCH_METADATA

        batch_metadata = DEFAULT_FIXTURE_BATCH_METADATA
        result = write_news_sentiment_handoff_jsonl(
            accepted_records,
            output_path,
            batch_metadata=batch_metadata,
            quarantine_path=quarantine_path,
        )
        records_written = result.records_written
        warnings.extend(result.warnings)
        rejection_reasons.extend(reason for item in result.rejection_reasons for reason in item.get("rejection_reasons", []))
    elif quarantine_path is not None and malformed_lines:
        quarantine_target = Path(quarantine_path)
        quarantine_target.parent.mkdir(parents=True, exist_ok=True)
        with quarantine_target.open("w", encoding="utf-8", newline="\n") as handle:
            for item in malformed_lines:
                handle.write(f"{item!r}\n")

    accepted_count = len(accepted_records)
    records_rejected = len(records) - accepted_count + len(malformed_lines)

    return NewsSentimentHandoffAcceptanceSummary(
        file_path=str(path),
        lines_read=len(records) + len(malformed_lines),
        records_parsed=len(records),
        records_accepted=accepted_count,
        records_written=records_written,
        records_rejected=records_rejected,
        malformed_lines=tuple(malformed_lines),
        rejection_reasons=tuple(dict.fromkeys(str(item) for item in rejection_reasons)),
        warnings=tuple(dict.fromkeys(str(item) for item in warnings)),
    )
