"""Validation helpers for cross-asset observations."""

from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Mapping, Sequence


@dataclass(frozen=True, slots=True)
class CrossAssetValidationError:
    field_name: str
    message: str


@dataclass(frozen=True, slots=True)
class CrossAssetValidationResult:
    is_valid: bool
    errors: tuple[CrossAssetValidationError, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


def _is_numeric(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_bool_or_none(value: object) -> bool:
    return value is None or isinstance(value, bool)


def _non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_cross_asset_observation(row: Mapping[str, object]) -> CrossAssetValidationResult:
    errors: list[CrossAssetValidationError] = []
    for field_name in ("observation_date", "source", "symbols", "descriptive_intermarket_state"):
        if field_name not in row:
            errors.append(CrossAssetValidationError(field_name, "field is required"))
    if not _non_empty_string(row.get("observation_date")):
        errors.append(CrossAssetValidationError("observation_date", "observation_date must be a non-empty string"))
    if not _non_empty_string(row.get("source")):
        errors.append(CrossAssetValidationError("source", "source must be a non-empty string"))
    if not isinstance(row.get("symbols"), list) or not row.get("symbols"):
        errors.append(CrossAssetValidationError("symbols", "symbols must be a non-empty list"))
    if not _non_empty_string(row.get("descriptive_intermarket_state")):
        errors.append(CrossAssetValidationError("descriptive_intermarket_state", "state must be a non-empty string"))

    for field_name in (
        "equity_leadership_score",
        "credit_risk_score",
        "rates_pressure_score",
        "dollar_pressure_score",
        "commodity_pressure_score",
        "volatility_pressure_score",
        "intermarket_alignment_score",
    ):
        value = row.get(field_name)
        if value is not None and not _is_numeric(value):
            errors.append(CrossAssetValidationError(field_name, "field must be numeric or None"))

    for field_name in ("risk_on_alignment_flag", "risk_off_alignment_flag", "divergence_flag"):
        value = row.get(field_name)
        if not _is_bool_or_none(value):
            errors.append(CrossAssetValidationError(field_name, "field must be boolean or None"))

    for field_name in ("quality_status", "certification_status", "freshness_status"):
        value = row.get(field_name)
        if value is not None and not _non_empty_string(value):
            errors.append(CrossAssetValidationError(field_name, "field must be a non-empty string when present"))

    return CrossAssetValidationResult(is_valid=not errors, errors=tuple(errors), warnings=())


def validate_cross_asset_observations(rows: Sequence[Mapping[str, object]]) -> list[CrossAssetValidationResult]:
    seen_keys: set[tuple[str, str]] = set()
    results: list[CrossAssetValidationResult] = []
    for row in rows:
        result = validate_cross_asset_observation(row)
        batch_key = (str(row.get("observation_date", "")).strip(), str(row.get("source", "")).strip())
        if batch_key in seen_keys:
            duplicate_error = CrossAssetValidationError("batch_key", "duplicate observation_date+source")
            result = CrossAssetValidationResult(is_valid=False, errors=tuple(result.errors) + (duplicate_error,), warnings=result.warnings)
        else:
            seen_keys.add(batch_key)
        results.append(result)
    return results