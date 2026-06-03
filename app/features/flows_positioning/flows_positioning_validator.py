"""Validation helpers for flows and positioning observations."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field


ALLOWED_LABELS = {
    "RISK_ON_FLOWS",
    "RISK_OFF_FLOWS",
    "CROWDED_LONG",
    "CROWDED_SHORT",
    "DEFENSIVE_ROTATION",
    "MIXED_POSITIONING",
    "LOW_SIGNAL_POSITIONING",
    "INSUFFICIENT_DATA",
}


@dataclass(frozen=True, slots=True)
class FlowsPositioningValidationError:
    field_name: str
    message: str


@dataclass(frozen=True, slots=True)
class FlowsPositioningValidationResult:
    is_valid: bool
    errors: tuple[FlowsPositioningValidationError, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


def _non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _numeric_or_none(value: object) -> bool:
    return value is None or isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_flows_positioning_observation(row):
    errors: list[FlowsPositioningValidationError] = []
    if not isinstance(row, Mapping):
        return FlowsPositioningValidationResult(False, (FlowsPositioningValidationError("row", "row must be a mapping"),), ())
    for field_name in ("observation_date", "source", "flow_regime_label"):
        if field_name not in row:
            errors.append(FlowsPositioningValidationError(field_name, "field is required"))
    if not _non_empty_string(row.get("observation_date")):
        errors.append(FlowsPositioningValidationError("observation_date", "observation_date must be a non-empty string"))
    if not _non_empty_string(row.get("source")):
        errors.append(FlowsPositioningValidationError("source", "source must be a non-empty string"))
    for field_name in (
        "equity_flow_score",
        "defensive_flow_score",
        "credit_flow_score",
        "options_positioning_score",
        "futures_positioning_score",
        "short_interest_pressure_score",
        "fund_exposure_score",
        "crowdedness_score",
        "positioning_risk_score",
    ):
        if field_name in row and not _numeric_or_none(row.get(field_name)):
            errors.append(FlowsPositioningValidationError(field_name, "field must be numeric or None"))
    label = row.get("flow_regime_label")
    if not _non_empty_string(label) or label not in ALLOWED_LABELS:
        errors.append(FlowsPositioningValidationError("flow_regime_label", "flow_regime_label must be an allowed non-empty label"))
    return FlowsPositioningValidationResult(is_valid=not errors, errors=tuple(errors), warnings=())


def validate_flows_positioning_observations(rows):
    errors: list[FlowsPositioningValidationError] = []
    seen: set[tuple[str, str]] = set()
    for index, row in enumerate(rows or []):
        result = validate_flows_positioning_observation(row)
        errors.extend(result.errors)
        if isinstance(row, Mapping) and _non_empty_string(row.get("observation_date")) and _non_empty_string(row.get("source")):
            key = (str(row["observation_date"]), str(row["source"]))
            if key in seen:
                errors.append(FlowsPositioningValidationError(f"rows[{index}]", "duplicate batch key observation_date + source"))
            seen.add(key)
    return FlowsPositioningValidationResult(is_valid=not errors, errors=tuple(errors), warnings=())
