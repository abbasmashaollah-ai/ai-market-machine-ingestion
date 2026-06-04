"""Validation helpers for market risk observations."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class MarketRiskValidationError:
    field_name: str
    message: str


@dataclass(frozen=True, slots=True)
class MarketRiskValidationResult:
    is_valid: bool
    errors: tuple[MarketRiskValidationError, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


ALLOWED_LABELS = (
    "LOW_MARKET_RISK",
    "NORMAL_MARKET_RISK",
    "ELEVATED_MARKET_RISK",
    "HIGH_MARKET_RISK",
    "EXTREME_MARKET_RISK",
    "MIXED_MARKET_RISK",
    "INSUFFICIENT_DATA",
)


def _is_numeric_or_none(value: object) -> bool:
    return value is None or (isinstance(value, (int, float)) and not isinstance(value, bool))


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_market_risk_observation(row: Mapping[str, object]) -> MarketRiskValidationResult:
    errors: list[MarketRiskValidationError] = []
    required = ("observation_date", "source", "market_risk_label")
    for field_name in required:
        if field_name not in row:
            errors.append(MarketRiskValidationError(field_name, "field is required"))

    for field_name in ("observation_date", "source"):
        if not _is_non_empty_string(row.get(field_name)):
            errors.append(MarketRiskValidationError(field_name, f"{field_name} must be a non-empty string"))

    if row.get("market_risk_label") not in ALLOWED_LABELS:
        errors.append(MarketRiskValidationError("market_risk_label", "market_risk_label must be an allowed label"))

    for field_name in (
        "volatility_risk_score",
        "options_risk_score",
        "positioning_risk_score",
        "event_risk_score",
        "sentiment_risk_score",
        "breadth_risk_score",
        "macro_liquidity_risk_score",
        "composite_market_risk_score",
    ):
        if not _is_numeric_or_none(row.get(field_name)):
            errors.append(MarketRiskValidationError(field_name, f"{field_name} must be numeric or None"))

    if not isinstance(row.get("price_states_by_symbol"), dict):
        errors.append(MarketRiskValidationError("price_states_by_symbol", "price_states_by_symbol must be an object"))

    return MarketRiskValidationResult(is_valid=not errors, errors=tuple(errors), warnings=())


def validate_market_risk_observations(rows: Sequence[Mapping[str, object]]) -> MarketRiskValidationResult:
    errors: list[MarketRiskValidationError] = []
    seen: set[tuple[object, object]] = set()
    for row in rows:
        result = validate_market_risk_observation(row)
        errors.extend(result.errors)
        key = (row.get("observation_date"), row.get("source"))
        if key in seen:
            errors.append(MarketRiskValidationError("observation_date+source", "duplicate batch key"))
        seen.add(key)
    return MarketRiskValidationResult(is_valid=not errors, errors=tuple(errors), warnings=())

