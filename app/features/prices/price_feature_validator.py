"""Validation helpers for price feature observations."""

from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Mapping, Sequence


ALLOWED_PRICE_TREND_STATES = {
    "STRONG_UPTREND",
    "UPTREND",
    "MIXED",
    "DOWNTREND",
    "STRONG_DOWNTREND",
    "INSUFFICIENT_DATA",
}


@dataclass(frozen=True, slots=True)
class PriceFeatureValidationError:
    field_name: str
    message: str


@dataclass(frozen=True, slots=True)
class PriceFeatureValidationResult:
    is_valid: bool
    errors: tuple[PriceFeatureValidationError, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


def _is_numeric(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_price_feature_observation(row: Mapping[str, object]) -> PriceFeatureValidationResult:
    errors: list[PriceFeatureValidationError] = []

    required_fields = ("symbol", "observation_date", "latest_close", "source")
    for field_name in required_fields:
        if field_name not in row:
            errors.append(PriceFeatureValidationError(field_name, "field is required"))

    symbol = row.get("symbol")
    latest_close = row.get("latest_close")

    if not _non_empty_string(symbol):
        errors.append(PriceFeatureValidationError("symbol", "symbol must be a non-empty string"))
    if not _is_numeric(latest_close) or float(latest_close) <= 0:
        errors.append(PriceFeatureValidationError("latest_close", "latest_close must be a positive numeric value"))

    numeric_or_none_fields = (
        "return_1d",
        "return_5d",
        "return_20d",
        "return_60d",
        "moving_average_20d",
        "moving_average_50d",
        "distance_from_ma_20d",
        "distance_from_ma_50d",
        "drawdown_from_20d_high",
        "drawdown_from_60d_high",
        "high_low_range_20d",
        "high_low_range_60d",
    )
    for field_name in numeric_or_none_fields:
        value = row.get(field_name)
        if value is not None and not _is_numeric(value):
            errors.append(PriceFeatureValidationError(field_name, "field must be numeric or None"))

    trend_state = row.get("price_trend_state")
    if trend_state is not None and trend_state not in ALLOWED_PRICE_TREND_STATES:
        errors.append(PriceFeatureValidationError("price_trend_state", "invalid price trend state"))

    for field_name in ("quality_status", "certification_status", "freshness_status"):
        value = row.get(field_name)
        if value is not None and not _non_empty_string(value):
            errors.append(PriceFeatureValidationError(field_name, "field must be a non-empty string when present"))

    for field_name in ("source",):
        if field_name in row and not _non_empty_string(row.get(field_name)):
            errors.append(PriceFeatureValidationError(field_name, "source must be a non-empty string"))

    is_valid = not errors
    return PriceFeatureValidationResult(is_valid=is_valid, errors=tuple(errors), warnings=())


def validate_price_feature_observations(rows: Sequence[Mapping[str, object]]) -> list[PriceFeatureValidationResult]:
    seen_keys: set[tuple[str, str, str]] = set()
    results: list[PriceFeatureValidationResult] = []
    for row in rows:
        result = validate_price_feature_observation(row)
        batch_key = (
            str(row.get("symbol", "")).strip().upper(),
            str(row.get("observation_date", "")).strip(),
            str(row.get("source", "")).strip(),
        )
        if batch_key in seen_keys:
            duplicate_error = PriceFeatureValidationError("batch_key", "duplicate symbol+observation_date+source")
            result = PriceFeatureValidationResult(
                is_valid=False,
                errors=tuple(result.errors) + (duplicate_error,),
                warnings=result.warnings,
            )
        else:
            seen_keys.add(batch_key)
        results.append(result)
    return results