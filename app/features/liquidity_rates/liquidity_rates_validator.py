"""Validation helpers for liquidity/rates observations."""

from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Mapping, Sequence


ALLOWED_LIQUIDITY_REGIME_LABELS = {
    "LIQUIDITY_TAILWIND",
    "LIQUIDITY_HEADWIND",
    "MIXED_LIQUIDITY",
    "TIGHT_FINANCIAL_CONDITIONS",
    "EASY_FINANCIAL_CONDITIONS",
    "INSUFFICIENT_DATA",
}


@dataclass(frozen=True, slots=True)
class LiquidityRatesValidationError:
    field_name: str
    message: str


@dataclass(frozen=True, slots=True)
class LiquidityRatesValidationResult:
    is_valid: bool
    errors: tuple[LiquidityRatesValidationError, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


def _is_numeric(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_liquidity_rates_observation(row: Mapping[str, object]) -> LiquidityRatesValidationResult:
    errors: list[LiquidityRatesValidationError] = []

    for field_name in ("observation_date", "source", "series", "liquidity_regime_label"):
        if field_name not in row:
            errors.append(LiquidityRatesValidationError(field_name, "field is required"))

    if not _non_empty_string(row.get("observation_date")):
        errors.append(LiquidityRatesValidationError("observation_date", "observation_date must be a non-empty string"))
    if not _non_empty_string(row.get("source")):
        errors.append(LiquidityRatesValidationError("source", "source must be a non-empty string"))
    if not isinstance(row.get("series"), list) or not row.get("series"):
        errors.append(LiquidityRatesValidationError("series", "series must be a non-empty list"))

    label = row.get("liquidity_regime_label")
    if label not in ALLOWED_LIQUIDITY_REGIME_LABELS:
        errors.append(LiquidityRatesValidationError("liquidity_regime_label", "invalid liquidity regime label"))

    for field_name in (
        "short_rate_pressure_score",
        "long_rate_pressure_score",
        "yield_curve_slope",
        "yield_curve_pressure_score",
        "real_yield_pressure_score",
        "dollar_liquidity_pressure_score",
        "credit_liquidity_score",
        "equity_liquidity_confirmation_score",
    ):
        value = row.get(field_name)
        if value is not None and not _is_numeric(value):
            errors.append(LiquidityRatesValidationError(field_name, "field must be numeric or None"))

    if row.get("quality_status") is not None and not _non_empty_string(row.get("quality_status")):
        errors.append(LiquidityRatesValidationError("quality_status", "field must be a non-empty string when present"))
    if row.get("certification_status") is not None and not _non_empty_string(row.get("certification_status")):
        errors.append(LiquidityRatesValidationError("certification_status", "field must be a non-empty string when present"))
    if row.get("freshness_status") is not None and not _non_empty_string(row.get("freshness_status")):
        errors.append(LiquidityRatesValidationError("freshness_status", "field must be a non-empty string when present"))

    return LiquidityRatesValidationResult(is_valid=not errors, errors=tuple(errors), warnings=())


def validate_liquidity_rates_observations(rows: Sequence[Mapping[str, object]]) -> list[LiquidityRatesValidationResult]:
    seen_keys: set[tuple[str, str]] = set()
    results: list[LiquidityRatesValidationResult] = []
    for row in rows:
        result = validate_liquidity_rates_observation(row)
        batch_key = (str(row.get("observation_date", "")).strip(), str(row.get("source", "")).strip())
        if batch_key in seen_keys:
            duplicate_error = LiquidityRatesValidationError("batch_key", "duplicate observation_date+source")
            result = LiquidityRatesValidationResult(is_valid=False, errors=tuple(result.errors) + (duplicate_error,), warnings=result.warnings)
        else:
            seen_keys.add(batch_key)
        results.append(result)
    return results