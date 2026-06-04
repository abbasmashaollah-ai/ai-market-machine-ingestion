"""Validation helpers for market regime observations."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class MarketRegimeValidationError:
    field_name: str
    message: str


@dataclass(frozen=True, slots=True)
class MarketRegimeValidationResult:
    is_valid: bool
    errors: tuple[MarketRegimeValidationError, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


ALLOWED_LABELS = (
    "RISK_ON_EXPANSION",
    "RISK_ON_FRAGILE",
    "NEUTRAL_MIXED",
    "DEFENSIVE_RISK_OFF",
    "STRESS_REGIME",
    "TRANSITION_REGIME",
    "INSUFFICIENT_DATA",
)


def _is_numeric_or_none(value: object) -> bool:
    return value is None or (isinstance(value, (int, float)) and not isinstance(value, bool))


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_market_regime_observation(row: Mapping[str, object]) -> MarketRegimeValidationResult:
    errors: list[MarketRegimeValidationError] = []
    required = ("observation_date", "source", "market_regime_label")
    for field_name in required:
        if field_name not in row:
            errors.append(MarketRegimeValidationError(field_name, "field is required"))

    for field_name in ("observation_date", "source"):
        if not _is_non_empty_string(row.get(field_name)):
            errors.append(MarketRegimeValidationError(field_name, f"{field_name} must be a non-empty string"))

    if row.get("market_regime_label") not in ALLOWED_LABELS:
        errors.append(MarketRegimeValidationError("market_regime_label", "market_regime_label must be an allowed label"))

    for field_name in (
        "liquidity_regime_score",
        "risk_regime_score",
        "participation_regime_score",
        "rotation_regime_score",
        "cross_asset_regime_score",
        "trend_regime_score",
        "volatility_regime_score",
        "composite_market_regime_score",
    ):
        if not _is_numeric_or_none(row.get(field_name)):
            errors.append(MarketRegimeValidationError(field_name, f"{field_name} must be numeric or None"))

    if not isinstance(row.get("price_states_by_symbol"), dict):
        errors.append(MarketRegimeValidationError("price_states_by_symbol", "price_states_by_symbol must be an object"))

    return MarketRegimeValidationResult(is_valid=not errors, errors=tuple(errors), warnings=())


def validate_market_regime_observations(rows: Sequence[Mapping[str, object]]) -> MarketRegimeValidationResult:
    errors: list[MarketRegimeValidationError] = []
    seen: set[tuple[object, object]] = set()
    for row in rows:
        result = validate_market_regime_observation(row)
        errors.extend(result.errors)
        key = (row.get("observation_date"), row.get("source"))
        if key in seen:
            errors.append(MarketRegimeValidationError("observation_date+source", "duplicate batch key"))
        seen.add(key)
    return MarketRegimeValidationResult(is_valid=not errors, errors=tuple(errors), warnings=())

