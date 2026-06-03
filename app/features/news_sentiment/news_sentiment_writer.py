"""Mock writer for news sentiment dry-run observations."""

from __future__ import annotations

from dataclasses import dataclass, field

from .news_sentiment_validator import NewsSentimentValidationError, validate_news_sentiment_observations


@dataclass(frozen=True, slots=True)
class NewsSentimentWriterResult:
    accepted_count: int
    rejected_count: int
    errors: tuple[NewsSentimentValidationError, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    no_db_writes: bool = True
    no_vendor_calls: bool = True
    no_scheduler_activation: bool = True


class NewsSentimentMockWriter:
    def __init__(self) -> None:
        self._rows: list[dict[str, object]] = []

    @property
    def rows(self) -> tuple[dict[str, object], ...]:
        return tuple(dict(row) for row in self._rows)

    def write(self, rows):
        rows_list = list(rows or [])
        validation = validate_news_sentiment_observations(rows_list)
        accepted_rows = []
        for row in rows_list:
            if isinstance(row, dict) and validate_news_sentiment_observations([row]).is_valid:
                accepted_rows.append(dict(row))
        self._rows.extend(accepted_rows)
        return NewsSentimentWriterResult(
            accepted_count=len(accepted_rows),
            rejected_count=max(0, len(rows_list) - len(accepted_rows)),
            errors=validation.errors,
            warnings=(),
        )


def write_news_sentiment_payloads(rows, writer=None):
    active_writer = writer or NewsSentimentMockWriter()
    return active_writer.write(rows)
