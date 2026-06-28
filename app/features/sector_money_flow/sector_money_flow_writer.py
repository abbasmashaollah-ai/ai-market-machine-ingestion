"""In-memory writer for sector money flow payloads."""

from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Mapping, Sequence

from .sector_money_flow_observation_builder import build_sector_money_flow_observations
from .sector_money_flow_validator import (
    SectorMoneyFlowValidationError,
    validate_sector_money_flow_observations,
)


@dataclass(frozen=True, slots=True)
class SectorMoneyFlowWriterResult:
    accepted_count: int
    rejected_count: int
    observation_payloads: tuple[dict[str, object], ...] = field(default_factory=tuple)
    errors: tuple[SectorMoneyFlowValidationError, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    no_db_writes: bool = True
    no_vendor_calls: bool = True
    no_scheduler_activation: bool = True


@dataclass
class SectorMoneyFlowMockWriter:
    observation_rows: list[dict[str, object]] = field(default_factory=list)

    def write(self, rows: Sequence[Mapping[str, object]] | None = None) -> SectorMoneyFlowWriterResult:
        rows = list(rows or [])
        built_rows = build_sector_money_flow_observations(rows)
        validation = validate_sector_money_flow_observations(built_rows)
        if validation.is_valid:
            self.observation_rows.extend(dict(row) for row in built_rows)
            return SectorMoneyFlowWriterResult(
                accepted_count=len(built_rows),
                rejected_count=0,
                observation_payloads=tuple(built_rows),
                warnings=tuple(validation.warnings),
            )
        return SectorMoneyFlowWriterResult(
            accepted_count=0,
            rejected_count=len(rows),
            errors=tuple(validation.errors),
            warnings=tuple(validation.warnings),
        )


def write_sector_money_flow_payloads(
    rows: Sequence[Mapping[str, object]] | None = None,
    writer: SectorMoneyFlowMockWriter | None = None,
) -> SectorMoneyFlowWriterResult:
    writer = writer or SectorMoneyFlowMockWriter()
    return writer.write(rows)
