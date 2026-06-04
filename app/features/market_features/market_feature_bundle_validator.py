"""Validation helpers for the market feature bundle dry-run output."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class MarketFeatureBundleValidationError:
    field_name: str
    message: str


@dataclass(frozen=True, slots=True)
class MarketFeatureBundleValidationResult:
    is_valid: bool
    errors: tuple[MarketFeatureBundleValidationError, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


def _non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_mapping(value: object) -> bool:
    return isinstance(value, Mapping)


def _validate_section_counts(section: Mapping[str, object], section_name: str, errors: list[MarketFeatureBundleValidationError]) -> None:
    for field_name in ("accepted_count", "rejected_count", "accepted_observation_count", "accepted_summary_count", "rejected_observation_count", "rejected_summary_count"):
        if field_name in section and not isinstance(section.get(field_name), int):
            errors.append(MarketFeatureBundleValidationError(f"{section_name}.{field_name}", "field must be an integer when present"))


def _section_label(section: Mapping[str, object], label_key: str) -> str | None:
    value = section.get(label_key)
    if isinstance(value, str) and value.strip():
        return value
    report = section.get("report")
    if isinstance(report, Mapping):
        value = report.get(label_key)
        if isinstance(value, str) and value.strip():
            return value
    return None


def validate_market_feature_bundle(bundle: Mapping[str, object]) -> MarketFeatureBundleValidationResult:
    errors: list[MarketFeatureBundleValidationError] = []

    required_fields = (
        "observation_date",
        "prices",
        "breadth",
        "sector_rotation",
        "cross_asset",
        "liquidity_rates",
        "volatility",
        "event_calendar",
        "news_sentiment",
        "earnings",
        "macro_liquidity",
        "market_risk",
        "fundamentals",
        "flows_positioning",
        "options",
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

    for section_name in ("prices", "breadth", "sector_rotation", "cross_asset", "liquidity_rates", "volatility", "event_calendar", "news_sentiment", "earnings", "macro_liquidity", "market_risk", "fundamentals", "flows_positioning", "options"):
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
            if _section_label(section, "participation_label") is None:
                errors.append(MarketFeatureBundleValidationError("breadth", "breadth must include a non-empty participation_label or report"))
        elif section_name == "sector_rotation":
            if _section_label(section, "descriptive_rotation_state") is None:
                errors.append(MarketFeatureBundleValidationError("sector_rotation", "sector_rotation must include a non-empty descriptive_rotation_state or report"))
        elif section_name == "cross_asset":
            if _section_label(section, "descriptive_intermarket_state") is None:
                errors.append(MarketFeatureBundleValidationError("cross_asset", "cross_asset must include a non-empty descriptive_intermarket_state or report"))
        elif section_name == "liquidity_rates":
            if _section_label(section, "liquidity_regime_label") is None:
                errors.append(MarketFeatureBundleValidationError("liquidity_rates", "liquidity_rates must include a non-empty liquidity_regime_label or report"))
        elif section_name == "volatility":
            if _section_label(section, "volatility_regime_label") is None:
                errors.append(MarketFeatureBundleValidationError("volatility", "volatility must include a non-empty volatility_regime_label or report"))
        elif section_name == "event_calendar":
            if _section_label(section, "event_risk_label") is None:
                errors.append(MarketFeatureBundleValidationError("event_calendar", "event_calendar must include a non-empty event_risk_label or report"))
        elif section_name == "news_sentiment":
            if _section_label(section, "sentiment_regime_label") is None:
                errors.append(MarketFeatureBundleValidationError("news_sentiment", "news_sentiment must include a non-empty sentiment_regime_label or report"))
        elif section_name == "earnings":
            reports = section.get("reports")
            reports_by_symbol = section.get("reports_by_symbol")
            labels = section.get("earnings_regime_labels_by_symbol")
            has_labels = isinstance(labels, Mapping) and any(_non_empty_string(value) for value in labels.values())
            has_reports = bool(reports) or bool(reports_by_symbol)
            if not has_labels and not has_reports:
                errors.append(MarketFeatureBundleValidationError("earnings", "earnings must include reports or earnings_regime_labels_by_symbol"))
        elif section_name == "macro_liquidity":
            if _section_label(section, "macro_liquidity_label") is None:
                errors.append(MarketFeatureBundleValidationError("macro_liquidity", "macro_liquidity must include a non-empty macro_liquidity_label or report"))
        elif section_name == "market_risk":
            if _section_label(section, "market_risk_label") is None:
                errors.append(MarketFeatureBundleValidationError("market_risk", "market_risk must include a non-empty market_risk_label or report"))
        elif section_name == "fundamentals":
            label_map = section.get("fundamental_quality_labels_by_symbol")
            reports = section.get("reports")
            reports_by_symbol = section.get("reports_by_symbol")
            has_label = isinstance(label_map, Mapping) and any(_non_empty_string(value) for value in label_map.values())
            has_reports = bool(reports) or bool(reports_by_symbol)
            if not has_label and not has_reports:
                errors.append(MarketFeatureBundleValidationError("fundamentals", "fundamentals must include reports or fundamental_quality_labels_by_symbol"))
        elif section_name == "flows_positioning":
            if _section_label(section, "flow_regime_label") is None:
                errors.append(MarketFeatureBundleValidationError("flows_positioning", "flows_positioning must include a non-empty flow_regime_label or report"))
        elif section_name == "options":
            if _section_label(section, "options_regime_label") is None:
                errors.append(MarketFeatureBundleValidationError("options", "options must include a non-empty options_regime_label or report"))

    return MarketFeatureBundleValidationResult(is_valid=not errors, errors=tuple(errors), warnings=())
