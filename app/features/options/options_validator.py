"""Validation helpers for options observations."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field


ALLOWED_LABELS = {
    "HIGH_VOLATILITY",
    "LOW_VOLATILITY",
    "MIXED_OPTIONS",
    "HEDGING_PRESSURE",
    "SKEWED_PROTECTIVE",
    "INSUFFICIENT_DATA",
}


@dataclass(frozen=True, slots=True)
class OptionsValidationError:
    field_name: str
    message: str


@dataclass(frozen=True, slots=True)
class OptionsValidationResult:
    is_valid: bool
    errors: tuple[OptionsValidationError, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


def _non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _numeric_or_none(value: object) -> bool:
    return value is None or isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_options_observation(row):
    errors: list[OptionsValidationError] = []
    if not isinstance(row, Mapping):
        return OptionsValidationResult(False, (OptionsValidationError("row", "row must be a mapping"),), ())
    for field_name in ("symbol", "observation_date", "source", "options_regime_label"):
        if field_name not in row:
            errors.append(OptionsValidationError(field_name, "field is required"))
    if not _non_empty_string(row.get("symbol")):
        errors.append(OptionsValidationError("symbol", "symbol must be a non-empty string"))
    if "underlying_symbol" in row and row.get("underlying_symbol") is not None and not _non_empty_string(row.get("underlying_symbol")):
        errors.append(OptionsValidationError("underlying_symbol", "underlying_symbol must be a non-empty string when provided"))
    if "expiration_date" in row and row.get("expiration_date") is not None and not _non_empty_string(row.get("expiration_date")):
        errors.append(OptionsValidationError("expiration_date", "expiration_date must be a non-empty string when provided"))
    if not _non_empty_string(row.get("observation_date")):
        errors.append(OptionsValidationError("observation_date", "observation_date must be a non-empty string"))
    if not _non_empty_string(row.get("source")):
        errors.append(OptionsValidationError("source", "source must be a non-empty string"))
    for field_name in (
        "implied_volatility_level",
        "realized_vs_implied_score",
        "iv_rank_score",
        "put_call_pressure_score",
        "call_pressure_score",
        "gamma_pressure_score",
        "skew_pressure_score",
        "iv_term_structure_score",
    ):
        if field_name in row and not _numeric_or_none(row.get(field_name)):
            errors.append(OptionsValidationError(field_name, "field must be numeric or None"))
    for field_name in ("total_volume", "total_open_interest"):
        if field_name in row:
            value = row.get(field_name)
            if not _numeric_or_none(value):
                errors.append(OptionsValidationError(field_name, "field must be numeric or None"))
            elif isinstance(value, (int, float)) and value < 0:
                errors.append(OptionsValidationError(field_name, "field must be non-negative when present"))
    label = row.get("options_regime_label")
    if not _non_empty_string(label) or label not in ALLOWED_LABELS:
        errors.append(OptionsValidationError("options_regime_label", "options_regime_label must be an allowed non-empty label"))
    return OptionsValidationResult(is_valid=not errors, errors=tuple(errors), warnings=())


def validate_options_observations(rows):
    errors: list[OptionsValidationError] = []
    seen: set[tuple[str, str, str]] = set()
    for index, row in enumerate(rows or []):
        result = validate_options_observation(row)
        errors.extend(result.errors)
        if isinstance(row, Mapping) and _non_empty_string(row.get("symbol")) and _non_empty_string(row.get("observation_date")) and _non_empty_string(row.get("source")):
            key = (str(row["symbol"]).upper(), str(row["observation_date"]), str(row["source"]))
            if key in seen:
                errors.append(OptionsValidationError(f"rows[{index}]", "duplicate batch key symbol + observation_date + source"))
            seen.add(key)
    return OptionsValidationResult(is_valid=not errors, errors=tuple(errors), warnings=())
