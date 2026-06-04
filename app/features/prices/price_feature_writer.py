"""Mock writer handoff for price feature dry runs."""

from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Mapping, Sequence
from copy import deepcopy

from app.features.prices.price_feature_validator import validate_price_feature_observations


@dataclass(frozen=True, slots=True)
class PriceFeatureWriterResult:
    accepted_count: int
    rejected_count: int
    errors: tuple[dict[str, object], ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    no_db_writes: bool = True
    no_vendor_calls: bool = True
    no_scheduler_activation: bool = True


class PriceFeatureMockWriter:
    def __init__(self) -> None:
        self._accepted_rows: list[dict[str, object]] = []

    @property
    def accepted_rows(self) -> list[dict[str, object]]:
        return [deepcopy(row) for row in self._accepted_rows]

    def write(self, rows: Sequence[Mapping[str, object]]) -> PriceFeatureWriterResult:
        normalized_rows = [dict(row) for row in rows]
        validations = validate_price_feature_observations(normalized_rows)
        errors: list[dict[str, object]] = []
        accepted_count = 0
        rejected_count = 0
        for row, validation in zip(normalized_rows, validations, strict=False):
            if validation.is_valid:
                self._accepted_rows.append(deepcopy(row))
                accepted_count += 1
            else:
                rejected_count += 1
                errors.append(
                    {
                        "symbol": row.get("symbol"),
                        "observation_date": row.get("observation_date"),
                        "source": row.get("source"),
                        "errors": [error.message for error in validation.errors],
                    }
                )
        return PriceFeatureWriterResult(
            accepted_count=accepted_count,
            rejected_count=rejected_count,
            errors=tuple(errors),
            warnings=(),
        )


def write_price_feature_payloads(rows: Sequence[Mapping[str, object]], writer: PriceFeatureMockWriter | None = None) -> PriceFeatureWriterResult:
    writer = writer or PriceFeatureMockWriter()
    return writer.write(rows)
