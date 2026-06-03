"""Deterministic validation helpers for sector rotation payloads."""

from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Mapping, Sequence

from app.features.sector_rotation.sector_rotation_summary_engine import determine_descriptive_rotation_state
from app.features.sector_rotation.sector_universe import get_sector_symbols, is_sector_symbol


@dataclass(frozen=True, slots=True)
class SectorRotationValidationError:
    code: str
    message: str
    field: str | None = None
    row_index: int | None = None


@dataclass(frozen=True, slots=True)
class SectorRotationValidationResult:
    is_valid: bool
    errors: tuple[SectorRotationValidationError, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


_ALLOWED_ROTATION_STATES = {
    "RISK_ON_LEADERSHIP",
    "DEFENSIVE_LEADERSHIP",
    "BROAD_IMPROVEMENT",
    "NARROW_LEADERSHIP",
    "BROAD_DETERIORATION",
    "MIXED_ROTATION",
    "NO_CLEAR_ROTATION",
}


def _error(code: str, message: str, field: str | None = None, row_index: int | None = None) -> SectorRotationValidationError:
    return SectorRotationValidationError(code=code, message=message, field=field, row_index=row_index)


def _is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_bool(value: object) -> bool:
    return isinstance(value, bool)


def _normalize_symbol(symbol: object) -> str:
    if not isinstance(symbol, str):
        return ""
    return symbol.strip().upper()


def _validate_required_fields(row: Mapping[str, object], required_fields: Sequence[str]) -> list[SectorRotationValidationError]:
    errors: list[SectorRotationValidationError] = []
    for field_name in required_fields:
        value = row.get(field_name)
        if value is None:
            errors.append(_error("missing_required_field", f"{field_name} is required", field=field_name))
            continue
        if isinstance(value, str) and not value.strip():
            errors.append(_error("missing_required_field", f"{field_name} is required", field=field_name))
    return errors


def validate_sector_rotation_observation(row: Mapping[str, object]) -> SectorRotationValidationResult:
    """Validate a single sector_rotation_observations payload."""

    errors = list(_validate_required_fields(row, ("universe", "sector", "sector_symbol", "observation_date", "close", "source")))
    warnings: list[str] = []
    sector_symbol = _normalize_symbol(row.get("sector_symbol"))

    if sector_symbol == "SPY":
        errors.append(_error("invalid_sector_symbol", "SPY is not valid as sector_symbol for sector_rotation_observations", field="sector_symbol"))
    elif sector_symbol and not is_sector_symbol(sector_symbol):
        errors.append(_error("invalid_sector_symbol", f"unknown sector_symbol: {sector_symbol}", field="sector_symbol"))

    close_value = row.get("close")
    if close_value is not None:
        if not _is_number(close_value) or float(close_value) <= 0:
            errors.append(_error("invalid_close", "close must be numeric and positive", field="close"))

    numeric_optional_fields = (
        "return_1d",
        "return_5d",
        "return_20d",
        "return_60d",
        "relative_strength_5d_vs_spy",
        "relative_strength_20d_vs_spy",
        "relative_strength_60d_vs_spy",
        "momentum_score",
    )
    for field_name in numeric_optional_fields:
        value = row.get(field_name)
        if value is not None and not _is_number(value):
            errors.append(_error("invalid_numeric_field", f"{field_name} must be numeric or None", field=field_name))

    rank_fields = ("rank_5d", "rank_20d", "rank_60d")
    for field_name in rank_fields:
        value = row.get(field_name)
        if value is not None and (not _is_int(value) or int(value) <= 0):
            errors.append(_error("invalid_rank", f"{field_name} must be a positive integer or None", field=field_name))

    rank_change_fields = ("rank_change_5d", "rank_change_20d")
    for field_name in rank_change_fields:
        value = row.get(field_name)
        if value is not None and not _is_int(value):
            errors.append(_error("invalid_rank_change", f"{field_name} must be an integer or None", field=field_name))

    boolean_optional_fields = ("leadership_flag", "deterioration_flag")
    for field_name in boolean_optional_fields:
        value = row.get(field_name)
        if value is not None and not _is_bool(value):
            errors.append(_error("invalid_flag", f"{field_name} must be boolean or None", field=field_name))

    boolean_fields = (
        "is_defensive_sector",
        "is_cyclical_sector",
        "is_growth_sector",
        "is_rate_sensitive_sector",
    )
    for field_name in boolean_fields:
        value = row.get(field_name)
        if not _is_bool(value):
            errors.append(_error("invalid_flag", f"{field_name} must be boolean", field=field_name))

    source = row.get("source")
    if not isinstance(source, str) or not source.strip():
        errors.append(_error("invalid_source", "source is required", field="source"))

    observation_date = row.get("observation_date")
    if not isinstance(observation_date, str) or not observation_date.strip():
        errors.append(_error("invalid_observation_date", "observation_date is required", field="observation_date"))

    return SectorRotationValidationResult(is_valid=not errors, errors=tuple(errors), warnings=tuple(warnings))


def validate_sector_rotation_observations(rows: Sequence[Mapping[str, object]]) -> SectorRotationValidationResult:
    """Validate a batch of sector_rotation_observations payloads."""

    errors: list[SectorRotationValidationError] = []
    warnings: list[str] = []
    seen: set[tuple[object, object, object, object]] = set()
    for index, row in enumerate(rows):
        result = validate_sector_rotation_observation(row)
        errors.extend(
            SectorRotationValidationError(
                code=error.code,
                message=error.message,
                field=error.field,
                row_index=index,
            )
            for error in result.errors
        )
        warnings.extend(result.warnings)
        key = (row.get("universe"), _normalize_symbol(row.get("sector_symbol")), row.get("observation_date"), row.get("source"))
        if key in seen:
            errors.append(_error("duplicate_row", "duplicate sector_rotation_observations key", row_index=index))
        else:
            seen.add(key)
    return SectorRotationValidationResult(is_valid=not errors, errors=tuple(errors), warnings=tuple(warnings))


def validate_sector_rotation_daily_summary(row: Mapping[str, object]) -> SectorRotationValidationResult:
    """Validate a single sector_rotation_daily_summary payload."""

    errors = list(_validate_required_fields(row, ("universe", "observation_date", "source")))
    warnings: list[str] = []

    numeric_optional_fields = (
        "risk_on_leadership_score",
        "defensive_leadership_score",
        "leadership_concentration_score",
        "sector_dispersion_score",
    )
    for field_name in numeric_optional_fields:
        value = row.get(field_name)
        if value is not None and not _is_number(value):
            errors.append(_error("invalid_numeric_field", f"{field_name} must be numeric or None", field=field_name))

    boolean_optional_fields = (
        "broad_rotation_flag",
        "narrow_rotation_flag",
        "improving_rotation_flag",
        "deteriorating_rotation_flag",
    )
    for field_name in boolean_optional_fields:
        value = row.get(field_name)
        if value is not None and not _is_bool(value):
            errors.append(_error("invalid_flag", f"{field_name} must be boolean or None", field=field_name))

    for field_name in ("top_sector_symbols", "bottom_sector_symbols"):
        value = row.get(field_name)
        if value is None:
            continue
        if not isinstance(value, (list, tuple)):
            errors.append(_error("invalid_symbol_list", f"{field_name} must be a list or tuple", field=field_name))
            continue
        for symbol in value:
            normalized = _normalize_symbol(symbol)
            if not normalized or not is_sector_symbol(normalized):
                errors.append(_error("invalid_symbol_list", f"{field_name} contains unknown sector symbol: {symbol!r}", field=field_name))

    state = row.get("descriptive_rotation_state")
    if state is not None and state not in _ALLOWED_ROTATION_STATES:
        errors.append(_error("invalid_rotation_state", "descriptive_rotation_state is invalid", field="descriptive_rotation_state"))

    source = row.get("source")
    if not isinstance(source, str) or not source.strip():
        errors.append(_error("invalid_source", "source is required", field="source"))

    observation_date = row.get("observation_date")
    if not isinstance(observation_date, str) or not observation_date.strip():
        errors.append(_error("invalid_observation_date", "observation_date is required", field="observation_date"))

    return SectorRotationValidationResult(is_valid=not errors, errors=tuple(errors), warnings=tuple(warnings))


def validate_sector_rotation_daily_summaries(rows: Sequence[Mapping[str, object]]) -> SectorRotationValidationResult:
    """Validate a batch of sector_rotation_daily_summary payloads."""

    errors: list[SectorRotationValidationError] = []
    warnings: list[str] = []
    seen: set[tuple[object, object, object]] = set()
    for index, row in enumerate(rows):
        result = validate_sector_rotation_daily_summary(row)
        errors.extend(
            SectorRotationValidationError(
                code=error.code,
                message=error.message,
                field=error.field,
                row_index=index,
            )
            for error in result.errors
        )
        warnings.extend(result.warnings)
        key = (row.get("universe"), row.get("observation_date"), row.get("source"))
        if key in seen:
            errors.append(_error("duplicate_row", "duplicate sector_rotation_daily_summary key", row_index=index))
        else:
            seen.add(key)
    return SectorRotationValidationResult(is_valid=not errors, errors=tuple(errors), warnings=tuple(warnings))
