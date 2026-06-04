"""Validation helpers for earnings observations."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class EarningsValidationError:
    field_name: str
    message: str


@dataclass(frozen=True, slots=True)
class EarningsValidationResult:
    is_valid: bool
    errors: tuple[EarningsValidationError, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


ALLOWED_LABELS = (
    "UPCOMING_EARNINGS_RISK",
    "POSITIVE_EARNINGS_REACTION",
    "NEGATIVE_EARNINGS_REACTION",
    "STRONG_EARNINGS_QUALITY",
    "WEAK_EARNINGS_QUALITY",
    "MIXED_EARNINGS",
    "LOW_EARNINGS_SIGNAL",
    "INSUFFICIENT_DATA",
)


def _is_numeric_or_none(value: object) -> bool:
    return value is None or (isinstance(value, (int, float)) and not isinstance(value, bool))


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_earnings_observation(row: Mapping[str, object]) -> EarningsValidationResult:
    errors: list[EarningsValidationError] = []
    required = ("symbol", "observation_date", "source", "earnings_regime_label")
    for field_name in required:
        if field_name not in row:
            errors.append(EarningsValidationError(field_name, "field is required"))

    for field_name in ("symbol", "observation_date", "source"):
        if not _is_non_empty_string(row.get(field_name)):
            errors.append(EarningsValidationError(field_name, f"{field_name} must be a non-empty string"))

    if row.get("earnings_regime_label") not in ALLOWED_LABELS:
        errors.append(EarningsValidationError("earnings_regime_label", "earnings_regime_label must be an allowed label"))

    for field_name in (
        "eps_surprise_score",
        "revenue_surprise_score",
        "guidance_score",
        "estimate_revision_score",
        "pre_earnings_drift_score",
        "post_earnings_reaction_score",
        "implied_vs_actual_move_score",
        "earnings_quality_score",
        "earnings_risk_score",
    ):
        if not _is_numeric_or_none(row.get(field_name)):
            errors.append(EarningsValidationError(field_name, f"{field_name} must be numeric or None"))

    for field_name in ("days_to_earnings", "days_since_earnings"):
        value = row.get(field_name)
        if value is not None and not isinstance(value, int):
            errors.append(EarningsValidationError(field_name, f"{field_name} must be an integer or None"))

    for field_name in ("source_attribution", "dataset_version", "created_at", "updated_at"):
        value = row.get(field_name)
        if value is not None and not _is_non_empty_string(value):
            errors.append(EarningsValidationError(field_name, f"{field_name} must be a non-empty string"))

    return EarningsValidationResult(is_valid=not errors, errors=tuple(errors), warnings=())


def validate_earnings_observations(rows: Sequence[Mapping[str, object]]) -> EarningsValidationResult:
    errors: list[EarningsValidationError] = []
    seen: set[tuple[object, object, object]] = set()
    for row in rows:
        result = validate_earnings_observation(row)
        errors.extend(result.errors)
        key = (row.get("symbol"), row.get("observation_date"), row.get("source"))
        if key in seen:
            errors.append(EarningsValidationError("symbol+observation_date+source", "duplicate batch key"))
        seen.add(key)
    return EarningsValidationResult(is_valid=not errors, errors=tuple(errors), warnings=())

