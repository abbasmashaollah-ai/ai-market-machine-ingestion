"""Mock writer for volatility dry-run payloads."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from copy import deepcopy

from app.features.volatility.volatility_validator import validate_volatility_observations


@dataclass(frozen=True, slots=True)
class VolatilityWriterResult:
    accepted_count: int
    rejected_count: int
    errors: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    no_db_writes: bool = True
    no_vendor_calls: bool = True
    no_scheduler_activation: bool = True


class VolatilityMockWriter:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def write(self, rows):
        self.rows.extend(deepcopy(list(rows)))


def write_volatility_payloads(rows: Sequence[dict[str, object]], writer: VolatilityMockWriter | None = None) -> VolatilityWriterResult:
    payloads = deepcopy(list(rows))
    validation_result = validate_volatility_observations(payloads)
    writer = writer or VolatilityMockWriter()
    if validation_result.is_valid:
        writer.write(payloads)
        return VolatilityWriterResult(accepted_count=len(payloads), rejected_count=0)
    return VolatilityWriterResult(
        accepted_count=0,
        rejected_count=len(payloads),
        errors=tuple(f"{error.field_name}: {error.message}" for error in validation_result.errors),
    )
