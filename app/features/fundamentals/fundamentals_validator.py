"""Validation helpers for fundamentals observations."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from .fundamentals_engine import determine_fundamental_quality_label


ALLOWED_LABELS = {
    "STRONG_FUNDAMENTALS",
    "HEALTHY_FUNDAMENTALS",
    "MIXED_FUNDAMENTALS",
    "WEAK_FUNDAMENTALS",
    "DISTRESSED_FUNDAMENTALS",
    "INSUFFICIENT_DATA",
}


@dataclass(frozen=True, slots=True)
class FundamentalValidationError:
    field_name: str
    message: str


@dataclass(frozen=True, slots=True)
class FundamentalValidationResult:
    is_valid: bool
    errors: tuple[FundamentalValidationError, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


def _non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _numeric_or_none(value: object) -> bool:
    return value is None or isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_fundamental_observation(row):
    errors: list[FundamentalValidationError] = []
    if not isinstance(row, Mapping):
        return FundamentalValidationResult(False, (FundamentalValidationError("row", "row must be a mapping"),), ())
    for field_name in ("symbol", "observation_date", "source", "fundamental_quality_label"):
        if field_name not in row:
            errors.append(FundamentalValidationError(field_name, "field is required"))
    if not _non_empty_string(row.get("symbol")):
        errors.append(FundamentalValidationError("symbol", "symbol must be a non-empty string"))
    if not _non_empty_string(row.get("observation_date")):
        errors.append(FundamentalValidationError("observation_date", "observation_date must be a non-empty string"))
    if not _non_empty_string(row.get("source")):
        errors.append(FundamentalValidationError("source", "source must be a non-empty string"))
    for field_name in ("growth_score", "profitability_score", "balance_sheet_score", "valuation_score", "cash_flow_score", "composite_fundamental_score"):
        if field_name in row and not _numeric_or_none(row.get(field_name)):
            errors.append(FundamentalValidationError(field_name, "field must be numeric or None"))
    label = row.get("fundamental_quality_label")
    if not _non_empty_string(label) or label not in ALLOWED_LABELS:
        errors.append(FundamentalValidationError("fundamental_quality_label", "fundamental_quality_label must be an allowed non-empty label"))
    return FundamentalValidationResult(is_valid=not errors, errors=tuple(errors), warnings=())


def validate_fundamental_observations(rows):
    errors: list[FundamentalValidationError] = []
    seen: set[tuple[str, str, str]] = set()
    for index, row in enumerate(rows or []):
        result = validate_fundamental_observation(row)
        errors.extend(result.errors)
        if isinstance(row, Mapping) and _non_empty_string(row.get("symbol")) and _non_empty_string(row.get("observation_date")) and _non_empty_string(row.get("source")):
            key = (str(row["symbol"]).upper(), str(row["observation_date"]), str(row["source"]))
            if key in seen:
                errors.append(FundamentalValidationError(f"rows[{index}]", "duplicate batch key symbol + observation_date + source"))
            seen.add(key)
    return FundamentalValidationResult(is_valid=not errors, errors=tuple(errors), warnings=())
