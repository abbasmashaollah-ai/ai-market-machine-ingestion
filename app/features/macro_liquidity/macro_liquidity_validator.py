"""Validation helpers for macro liquidity observations."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class MacroLiquidityValidationError:
    field_name: str
    message: str


@dataclass(frozen=True, slots=True)
class MacroLiquidityValidationResult:
    is_valid: bool
    errors: tuple[MacroLiquidityValidationError, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


ALLOWED_LABELS = (
    "STRONG_LIQUIDITY_TAILWIND",
    "LIQUIDITY_TAILWIND",
    "MIXED_MACRO_LIQUIDITY",
    "LIQUIDITY_HEADWIND",
    "STRONG_LIQUIDITY_HEADWIND",
    "INSUFFICIENT_DATA",
)


def _is_numeric_or_none(value: object) -> bool:
    return value is None or (isinstance(value, (int, float)) and not isinstance(value, bool))


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_macro_liquidity_observation(row: Mapping[str, object]) -> MacroLiquidityValidationResult:
    errors: list[MacroLiquidityValidationError] = []
    required = ("observation_date", "source", "macro_liquidity_label")
    for field_name in required:
        if field_name not in row:
            errors.append(MacroLiquidityValidationError(field_name, "field is required"))

    for field_name in ("observation_date", "source"):
        if not _is_non_empty_string(row.get(field_name)):
            errors.append(MacroLiquidityValidationError(field_name, f"{field_name} must be a non-empty string"))

    if row.get("macro_liquidity_label") not in ALLOWED_LABELS:
        errors.append(MacroLiquidityValidationError("macro_liquidity_label", "macro_liquidity_label must be an allowed label"))

    for field_name in (
        "rates_liquidity_pressure_score",
        "cross_asset_confirmation_score",
        "positioning_liquidity_score",
        "volatility_liquidity_stress_score",
        "participation_confirmation_score",
        "composite_macro_liquidity_score",
    ):
        if not _is_numeric_or_none(row.get(field_name)):
            errors.append(MacroLiquidityValidationError(field_name, f"{field_name} must be numeric or None"))

    return MacroLiquidityValidationResult(is_valid=not errors, errors=tuple(errors), warnings=())


def validate_macro_liquidity_observations(rows: Sequence[Mapping[str, object]]) -> MacroLiquidityValidationResult:
    errors: list[MacroLiquidityValidationError] = []
    seen: set[tuple[object, object]] = set()
    for row in rows:
        result = validate_macro_liquidity_observation(row)
        errors.extend(result.errors)
        key = (row.get("observation_date"), row.get("source"))
        if key in seen:
            errors.append(MacroLiquidityValidationError("observation_date+source", "duplicate batch key"))
        seen.add(key)
    return MacroLiquidityValidationResult(is_valid=not errors, errors=tuple(errors), warnings=())

