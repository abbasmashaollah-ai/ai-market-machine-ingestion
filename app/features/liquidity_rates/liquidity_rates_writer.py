"""Mock writer handoff for liquidity/rates dry runs."""

from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Mapping, Sequence
from copy import deepcopy

from app.features.liquidity_rates.liquidity_rates_validator import validate_liquidity_rates_observation


@dataclass(frozen=True, slots=True)
class LiquidityRatesWriterResult:
    accepted_count: int
    rejected_count: int
    errors: tuple[dict[str, object], ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    no_db_writes: bool = True
    no_vendor_calls: bool = True
    no_scheduler_activation: bool = True


class LiquidityRatesMockWriter:
    def __init__(self) -> None:
        self._accepted_rows: list[dict[str, object]] = []

    @property
    def accepted_rows(self) -> list[dict[str, object]]:
        return [deepcopy(row) for row in self._accepted_rows]

    def write(self, rows: Sequence[Mapping[str, object]]) -> LiquidityRatesWriterResult:
        errors: list[dict[str, object]] = []
        accepted_count = 0
        rejected_count = 0
        for row in rows:
            validation = validate_liquidity_rates_observation(row)
            if validation.is_valid:
                self._accepted_rows.append(deepcopy(dict(row)))
                accepted_count += 1
            else:
                rejected_count += 1
                errors.append(
                    {
                        "observation_date": row.get("observation_date"),
                        "source": row.get("source"),
                        "errors": [error.message for error in validation.errors],
                    }
                )
        return LiquidityRatesWriterResult(
            accepted_count=accepted_count,
            rejected_count=rejected_count,
            errors=tuple(errors),
            warnings=(),
        )


def write_liquidity_rates_payloads(rows: Sequence[Mapping[str, object]], writer: LiquidityRatesMockWriter | None = None) -> LiquidityRatesWriterResult:
    writer = writer or LiquidityRatesMockWriter()
    return writer.write(rows)