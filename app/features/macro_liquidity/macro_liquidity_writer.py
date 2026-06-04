"""Mock writer for macro liquidity dry-run payloads."""

from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy
from dataclasses import dataclass, field

from app.features.macro_liquidity.macro_liquidity_validator import validate_macro_liquidity_observations


@dataclass(frozen=True, slots=True)
class MacroLiquidityWriterResult:
    accepted_count: int
    rejected_count: int
    errors: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    no_db_writes: bool = True
    no_vendor_calls: bool = True
    no_scheduler_activation: bool = True


class MacroLiquidityMockWriter:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def write(self, rows):
        self.rows.extend(deepcopy(list(rows)))


def write_macro_liquidity_payloads(rows: Sequence[dict[str, object]], writer: MacroLiquidityMockWriter | None = None) -> MacroLiquidityWriterResult:
    payloads = deepcopy(list(rows))
    validation_result = validate_macro_liquidity_observations(payloads)
    writer = writer or MacroLiquidityMockWriter()
    if validation_result.is_valid:
        writer.write(payloads)
        return MacroLiquidityWriterResult(accepted_count=len(payloads), rejected_count=0)
    return MacroLiquidityWriterResult(
        accepted_count=0,
        rejected_count=len(payloads),
        errors=tuple(f"{error.field_name}: {error.message}" for error in validation_result.errors),
    )

