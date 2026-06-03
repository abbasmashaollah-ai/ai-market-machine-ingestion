"""Validation helpers for the market feature bundle dry-run output."""

from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Mapping, Sequence


@dataclass(frozen=True, slots=True)
class MarketFeatureBundleValidationError:
    field_name: str
    message: str


@dataclass(frozen=True, slots=True)
class MarketFeatureBundleValidationResult:
    is_valid: bool
    errors: tuple[MarketFeatureBundleValidationError, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


def _is_bool(value: object) -> bool:
    return isinstance(value, bool)


def _non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_mapping(value: object) -> bool:
    return isinstance(value, Mapping)


def _validate_section_counts(section: Mapping[str, object], section_name: str, errors: list[MarketFeatureBundleValidationError]) -> None:
    for field_name in ("accepted_count", "rejected_count", "accepted_observation_count", "accepted_summary_count", "rejected_observation_count", "rejected_summary_count"):
        if field_name in section and not isinstance(section.get(field_name), int):
            errors.append(MarketFeatureBundleValidationError(f"{section_name}.{field_name}", "field must be an integer when present"))


def validate_market_feature_bundle(bundle: Mapping[str, object]) -> MarketFeatureBundleValidationResult:
    errors: list[MarketFeatureBundleValidationError] = []

    required_fields = (
        "observation_date",
        "prices",
        "breadth",
        "sector_rotation",
        "cross_asset",
        "warnings",
        "no_db_writes",
        "no_vendor_calls",
        "no_live_api_calls",
        "no_scheduler_activation",
    )
    for field_name in required_fields:
        if field_name not in bundle:
            errors.append(MarketFeatureBundleValidationError(field_name, "field is required"))

    if not _non_empty_string(bundle.get("observation_date")):
        errors.append(MarketFeatureBundleValidationError("observation_date", "observation_date must be a non-empty string"))

    for field_name in ("no_db_writes", "no_vendor_calls", "no_live_api_calls", "no_scheduler_activation"):
        if bundle.get(field_name) is not True:
            errors.append(MarketFeatureBundleValidationError(field_name, "field must be True"))

    warnings_value = bundle.get("warnings")
    if warnings_value is not None and not isinstance(warnings_value, list):
        errors.append(MarketFeatureBundleValidationError("warnings", "warnings must be a list when present"))

    for section_name in ("prices", "breadth", "sector_rotation", "cross_asset"):
        section = bundle.get(section_name)
        if not _is_mapping(section):
            errors.append(MarketFeatureBundleValidationError(section_name, "field must be an object"))
            continue

        _validate_section_counts(section, section_name, errors)

        if section_name == "prices":
            has_reports = bool(section.get("reports")) or bool(section.get("reports_by_symbol"))
            if not has_reports:
                errors.append(MarketFeatureBundleValidationError("prices", "prices must include reports or reports_by_symbol"))
        elif section_name == "breadth":
            if "participation_label" not in section and not _is_mapping(section.get("report")):
                errors.append(MarketFeatureBundleValidationError("breadth", "breadth must include participation_label or report"))
        elif section_name == "sector_rotation":
            if "descriptive_rotation_state" not in section and not _is_mapping(section.get("report")):
                errors.append(MarketFeatureBundleValidationError("sector_rotation", "sector_rotation must include descriptive_rotation_state or report"))
        elif section_name == "cross_asset":
            if "descriptive_intermarket_state" not in section and not _is_mapping(section.get("report")):
                errors.append(MarketFeatureBundleValidationError("cross_asset", "cross_asset must include descriptive_intermarket_state or report"))

    return MarketFeatureBundleValidationResult(is_valid=not errors, errors=tuple(errors), warnings=())