"""Mock writer handoff for validated sector rotation payloads."""

from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Mapping, Sequence

from app.features.sector_rotation.sector_rotation_validator import (
    SectorRotationValidationError,
    SectorRotationValidationResult,
    validate_sector_rotation_daily_summaries,
    validate_sector_rotation_observations,
)


@dataclass(frozen=True, slots=True)
class SectorRotationWriterResult:
    accepted_observation_count: int
    accepted_summary_count: int
    rejected_observation_count: int
    rejected_summary_count: int
    errors: tuple[SectorRotationValidationError, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    no_db_writes: bool = True
    no_vendor_calls: bool = True
    no_scheduler_activation: bool = True


@dataclass
class SectorRotationMockWriter:
    """In-memory writer proof only.

    Accepted rows are retained only in local Python memory.
    """

    observation_rows: list[dict[str, object]] = field(default_factory=list)
    summary_rows: list[dict[str, object]] = field(default_factory=list)

    def write(
        self,
        observation_rows: Sequence[Mapping[str, object]] | None = None,
        summary_rows: Sequence[Mapping[str, object]] | None = None,
    ) -> SectorRotationWriterResult:
        observation_rows = list(observation_rows or [])
        summary_rows = list(summary_rows or [])

        observation_validation = validate_sector_rotation_observations(observation_rows)
        summary_validation = validate_sector_rotation_daily_summaries(summary_rows)

        errors = list(observation_validation.errors) + list(summary_validation.errors)
        warnings = list(observation_validation.warnings) + list(summary_validation.warnings)

        accepted_observation_count = 0
        accepted_summary_count = 0
        rejected_observation_count = 0
        rejected_summary_count = 0

        if observation_validation.is_valid:
            self.observation_rows.extend(dict(row) for row in observation_rows)
            accepted_observation_count = len(observation_rows)
        else:
            rejected_observation_count = len(observation_rows)

        if summary_validation.is_valid:
            self.summary_rows.extend(dict(row) for row in summary_rows)
            accepted_summary_count = len(summary_rows)
        else:
            rejected_summary_count = len(summary_rows)

        return SectorRotationWriterResult(
            accepted_observation_count=accepted_observation_count,
            accepted_summary_count=accepted_summary_count,
            rejected_observation_count=rejected_observation_count,
            rejected_summary_count=rejected_summary_count,
            errors=tuple(errors),
            warnings=tuple(warnings),
        )


def write_sector_rotation_payloads(
    observation_rows: Sequence[Mapping[str, object]] | None = None,
    summary_rows: Sequence[Mapping[str, object]] | None = None,
    writer: SectorRotationMockWriter | None = None,
) -> SectorRotationWriterResult:
    """Validate and stage payloads in memory only."""

    writer = writer or SectorRotationMockWriter()
    return writer.write(observation_rows=observation_rows, summary_rows=summary_rows)
