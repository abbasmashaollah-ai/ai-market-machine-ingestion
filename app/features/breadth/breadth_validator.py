"""Validation helpers for breadth observations."""

from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Mapping, Sequence


@dataclass(frozen=True, slots=True)
class BreadthValidationError:
    field_name: str
    message: str


@dataclass(frozen=True, slots=True)
class BreadthValidationResult:
    is_valid: bool
    errors: tuple[BreadthValidationError, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_numeric(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_breadth_observation(row: Mapping[str, object]) -> BreadthValidationResult:
    errors: list[BreadthValidationError] = []
    required_fields = ("universe", "observation_date", "source", "advancers", "decliners", "unchanged")
    for field_name in required_fields:
        if field_name not in row:
            errors.append(BreadthValidationError(field_name, "field is required"))

    if not _non_empty_string(row.get("universe")):
        errors.append(BreadthValidationError("universe", "universe must be a non-empty string"))
    if not _non_empty_string(row.get("source")):
        errors.append(BreadthValidationError("source", "source must be a non-empty string"))

    for field_name in ("advancers", "decliners", "unchanged", "new_highs", "new_lows"):
        value = row.get(field_name)
        if value is not None and (not _is_integer(value) or value < 0):
            errors.append(BreadthValidationError(field_name, "field must be a non-negative integer"))

    for field_name in ("percent_above_20d", "percent_above_50d", "percent_above_200d", "breadth_score", "participation_score", "advancing_volume", "declining_volume"):
        value = row.get(field_name)
        if value is not None and not _is_numeric(value):
            errors.append(BreadthValidationError(field_name, "field must be numeric or None"))

    for field_name in ("quality_status", "certification_status", "freshness_status"):
        value = row.get(field_name)
        if value is not None and not _non_empty_string(value):
            errors.append(BreadthValidationError(field_name, "field must be a non-empty string when present"))

    return BreadthValidationResult(is_valid=not errors, errors=tuple(errors), warnings=())


def validate_breadth_observations(rows: Sequence[Mapping[str, object]]) -> list[BreadthValidationResult]:
    seen_keys: set[tuple[str, str, str]] = set()
    results: list[BreadthValidationResult] = []
    for row in rows:
        result = validate_breadth_observation(row)
        batch_key = (
            str(row.get("universe", "")).strip(),
            str(row.get("observation_date", "")).strip(),
            str(row.get("source", "")).strip(),
        )
        if batch_key in seen_keys:
            duplicate_error = BreadthValidationError("batch_key", "duplicate universe+observation_date+source")
            result = BreadthValidationResult(is_valid=False, errors=tuple(result.errors) + (duplicate_error,), warnings=result.warnings)
        else:
            seen_keys.add(batch_key)
        results.append(result)
    return results
