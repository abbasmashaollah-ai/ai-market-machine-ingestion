"""Validation helpers for volatility observations."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class VolatilityValidationError:
    field_name: str
    message: str


@dataclass(frozen=True, slots=True)
class VolatilityValidationResult:
    is_valid: bool
    errors: tuple[VolatilityValidationError, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


ALLOWED_LABELS = (
    "LOW_VOLATILITY",
    "NORMAL_VOLATILITY",
    "ELEVATED_VOLATILITY",
    "HIGH_VOLATILITY",
    "EXTREME_VOLATILITY",
    "MIXED_VOLATILITY",
    "INSUFFICIENT_DATA",
)


def _is_mapping(value: object) -> bool:
    return isinstance(value, Mapping)


def _is_numeric_or_none(value: object) -> bool:
    return value is None or (isinstance(value, (int, float)) and not isinstance(value, bool))


def validate_volatility_observation(row: Mapping[str, object]) -> VolatilityValidationResult:
    errors: list[VolatilityValidationError] = []
    required = ("observation_date", "source", "series", "volatility_regime_label")
    for field_name in required:
        if field_name not in row:
            errors.append(VolatilityValidationError(field_name, "field is required"))

    series = row.get("series")
    if not isinstance(series, list):
        errors.append(VolatilityValidationError("series", "series must be a list"))

    if row.get("volatility_regime_label") not in ALLOWED_LABELS:
        errors.append(VolatilityValidationError("volatility_regime_label", "volatility_regime_label must be an allowed label"))

    for field_name in (
        "vix_level",
        "vvix_level",
        "vxn_level",
        "rvx_level",
        "vix_change_1d",
        "vix_change_5d",
        "vix_change_20d",
        "vvix_change_5d",
        "volatility_of_volatility_score",
        "equity_volatility_pressure_score",
        "nasdaq_volatility_pressure_score",
        "small_cap_volatility_pressure_score",
        "composite_volatility_stress_score",
    ):
        if not _is_numeric_or_none(row.get(field_name)):
            errors.append(VolatilityValidationError(field_name, "field must be numeric or None"))

    return VolatilityValidationResult(is_valid=not errors, errors=tuple(errors), warnings=())


def validate_volatility_observations(rows: Sequence[Mapping[str, object]]) -> VolatilityValidationResult:
    errors: list[VolatilityValidationError] = []
    seen: set[tuple[object, object]] = set()
    for row in rows:
        result = validate_volatility_observation(row)
        errors.extend(result.errors)
        key = (row.get("observation_date"), row.get("source"))
        if key in seen:
            errors.append(VolatilityValidationError("observation_date+source", "duplicate batch key"))
        seen.add(key)
    return VolatilityValidationResult(is_valid=not errors, errors=tuple(errors), warnings=())
