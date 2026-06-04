"""Mock writer for market regime dry-run payloads."""

from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy
from dataclasses import dataclass, field

from app.features.market_regime.market_regime_validator import validate_market_regime_observations


@dataclass(frozen=True, slots=True)
class MarketRegimeWriterResult:
    accepted_count: int
    rejected_count: int
    errors: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    no_db_writes: bool = True
    no_vendor_calls: bool = True
    no_scheduler_activation: bool = True


class MarketRegimeMockWriter:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def write(self, rows):
        self.rows.extend(deepcopy(list(rows)))


def write_market_regime_payloads(rows: Sequence[dict[str, object]], writer: MarketRegimeMockWriter | None = None) -> MarketRegimeWriterResult:
    payloads = deepcopy(list(rows))
    validation_result = validate_market_regime_observations(payloads)
    writer = writer or MarketRegimeMockWriter()
    if validation_result.is_valid:
        writer.write(payloads)
        return MarketRegimeWriterResult(accepted_count=len(payloads), rejected_count=0)
    return MarketRegimeWriterResult(
        accepted_count=0,
        rejected_count=len(payloads),
        errors=tuple(f"{error.field_name}: {error.message}" for error in validation_result.errors),
    )

