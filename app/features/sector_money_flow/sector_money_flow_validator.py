"""Deterministic validation helpers for sector money flow payloads."""

from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Mapping, Sequence


@dataclass(frozen=True, slots=True)
class SectorMoneyFlowValidationError:
    code: str
    message: str
    field: str | None = None
    row_index: int | None = None


@dataclass(frozen=True, slots=True)
class SectorMoneyFlowValidationResult:
    is_valid: bool
    errors: tuple[SectorMoneyFlowValidationError, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


_REQUIRED_FIELDS = ("observation_date", "sector_symbol", "source_vendor", "source_dataset", "source_sha256", "generated_at", "schema_version", "idempotency_key", "metadata")
_SIGNAL_FIELDS = {
    "buy_signal",
    "sell_signal",
    "trading_signal",
    "recommendation",
    "portfolio_allocation",
    "ai_signal",
}
_UNSUPPORTED_INSTITUTIONAL_FIELDS = {
    "institutional_inflow",
    "institutional_outflow",
    "institutional_flow",
    "smart_money_flow",
}


def _error(code: str, message: str, field: str | None = None, row_index: int | None = None) -> SectorMoneyFlowValidationError:
    return SectorMoneyFlowValidationError(code=code, message=message, field=field, row_index=row_index)


def _is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _normalize_text(value: object | None) -> str:
    return str(value).strip() if value is not None else ""


def _validate_required_fields(row: Mapping[str, object], required_fields: Sequence[str]) -> list[SectorMoneyFlowValidationError]:
    errors: list[SectorMoneyFlowValidationError] = []
    for field_name in required_fields:
        value = row.get(field_name)
        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append(_error("missing_required_field", f"{field_name} is required", field=field_name))
    return errors


def validate_sector_money_flow_observation(row: Mapping[str, object]) -> SectorMoneyFlowValidationResult:
    errors = list(_validate_required_fields(row, _REQUIRED_FIELDS))
    warnings: list[str] = []

    if not _normalize_text(row.get("observation_date")):
        errors.append(_error("invalid_observation_date", "observation_date is required", field="observation_date"))

    if not _normalize_text(row.get("sector_symbol")):
        errors.append(_error("invalid_sector_symbol", "sector_symbol is required", field="sector_symbol"))

    for field_name in ("sector_etf_volume_confirmed_move", "sector_etf_dollar_volume", "accumulation_distribution_proxy", "inflow_outflow_proxy", "flow_confidence", "flow_support_score"):
        value = row.get(field_name)
        if value is not None and not _is_number(value):
            errors.append(_error("invalid_numeric_field", f"{field_name} must be numeric or None", field=field_name))

    for field_name in _UNSUPPORTED_INSTITUTIONAL_FIELDS:
        if field_name in row and row.get(field_name) is not None:
            errors.append(_error("unsupported_institutional_flow_claim", f"{field_name} is not allowed as a canonical top-level field", field=field_name))

    for field_name in _SIGNAL_FIELDS:
        if field_name in row and row.get(field_name) is not None:
            errors.append(_error("unsupported_trading_signal", f"{field_name} is not allowed as a top-level field", field=field_name))

    for field_name in ("source_vendor", "source_dataset", "source_sha256", "generated_at", "schema_version", "idempotency_key"):
        if not _normalize_text(row.get(field_name)):
            errors.append(_error("missing_required_field", f"{field_name} is required", field=field_name))

    metadata = row.get("metadata")
    if not isinstance(metadata, Mapping):
        errors.append(_error("invalid_metadata", "metadata must be a mapping", field="metadata"))

    return SectorMoneyFlowValidationResult(is_valid=not errors, errors=tuple(errors), warnings=tuple(warnings))


def validate_sector_money_flow_observations(rows: Sequence[Mapping[str, object]]) -> SectorMoneyFlowValidationResult:
    errors: list[SectorMoneyFlowValidationError] = []
    warnings: list[str] = []
    seen: set[tuple[object, object, object, object, object]] = set()
    for index, row in enumerate(rows):
        result = validate_sector_money_flow_observation(row)
        errors.extend(
            SectorMoneyFlowValidationError(
                code=error.code,
                message=error.message,
                field=error.field,
                row_index=index,
            )
            for error in result.errors
        )
        warnings.extend(result.warnings)
        key = (
            row.get("source_vendor"),
            row.get("source_dataset"),
            row.get("source_sha256"),
            row.get("observation_date"),
            _normalize_text(row.get("sector_symbol")),
        )
        if key in seen:
            errors.append(_error("duplicate_row", "duplicate sector_money_flow key", row_index=index))
        else:
            seen.add(key)
    return SectorMoneyFlowValidationResult(is_valid=not errors, errors=tuple(errors), warnings=tuple(warnings))
