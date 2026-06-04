"""Mock writer for options observations."""

from __future__ import annotations

from dataclasses import dataclass, field

from .options_validator import OptionsValidationError, validate_options_observations


@dataclass(frozen=True, slots=True)
class OptionsWriterResult:
    accepted_count: int
    rejected_count: int
    errors: tuple[OptionsValidationError, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    no_db_writes: bool = True
    no_vendor_calls: bool = True
    no_scheduler_activation: bool = True


class OptionsMockWriter:
    def __init__(self) -> None:
        self._rows: list[dict[str, object]] = []

    @property
    def rows(self) -> tuple[dict[str, object], ...]:
        return tuple(dict(row) for row in self._rows)

    def write(self, rows):
        rows_list = list(rows or [])
        validation = validate_options_observations(rows_list)
        accepted_rows = []
        for row in rows_list:
            if isinstance(row, dict) and validate_options_observations([row]).is_valid:
                accepted_rows.append(dict(row))
        self._rows.extend(accepted_rows)
        return OptionsWriterResult(
            accepted_count=len(accepted_rows),
            rejected_count=max(0, len(rows_list) - len(accepted_rows)),
            errors=validation.errors,
            warnings=(),
        )


def write_options_payloads(rows, writer=None):
    active_writer = writer or OptionsMockWriter()
    return active_writer.write(rows)
