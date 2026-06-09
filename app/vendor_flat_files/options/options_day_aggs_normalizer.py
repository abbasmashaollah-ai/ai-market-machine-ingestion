from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from .options_day_aggs_parser import ParsedOptionsContract, parse_opra_option_symbol, OptionsDayAggsParseError, OptionsDayAggsParseResult


@dataclass(frozen=True, slots=True)
class OptionsDayAggsNormalizationError:
    code: str
    message: str
    row_number: int | None = None
    field_name: str | None = None


@dataclass(frozen=True, slots=True)
class OptionsDayAggsNormalizationResult:
    normalization_status: str
    records: tuple[dict[str, object], ...] = field(default_factory=tuple)
    record_count: int = 0
    warnings: tuple[str, ...] = field(default_factory=tuple)
    errors: tuple[OptionsDayAggsNormalizationError, ...] = field(default_factory=tuple)
    source_file_sha256: str | None = None
    source_file_path: str | None = None


def _to_decimal(value: object) -> Decimal | None:
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _vendor_from_source(path: str | None) -> str:
    return "polygon_or_massive"


def _safe_int(value: object) -> int:
    return int(value) if value not in (None, "") else 0


def _maybe_issue_warning(warnings: list[str], *, row_number: int, contract: ParsedOptionsContract, high_value: object, low_value: object) -> None:
    if not contract.parse_ok:
        warnings.append(f"row {row_number}: {contract.warning or 'symbol parse failed'}")
    high = _to_decimal(high_value)
    low = _to_decimal(low_value)
    if high is not None and low is not None and high < low:
        warnings.append(f"row {row_number}: high lower than low")


def normalize_options_day_aggs_records(parsed: OptionsDayAggsParseResult, *, source: str = "local_quarantine", source_dataset: str = "us_options_opra/day_aggs_v1") -> OptionsDayAggsNormalizationResult:
    warnings: list[str] = list(parsed.warnings)
    errors: list[OptionsDayAggsNormalizationError] = []
    records: list[dict[str, object]] = []

    for parse_error in parsed.errors:
        errors.append(
            OptionsDayAggsNormalizationError(
                code=parse_error.code,
                message=parse_error.message,
                row_number=parse_error.row_number,
                field_name=parse_error.field_name,
            )
        )

    for row in parsed.rows:
        row_number = int(row.get("row_number") or 0)
        ticker = str(row.get("ticker") or "")
        contract: ParsedOptionsContract = parse_opra_option_symbol(ticker)
        open_value = row.get("open")
        high_value = row.get("high")
        low_value = row.get("low")
        close_value = row.get("close")
        volume = _safe_int(row.get("volume"))
        transactions = _safe_int(row.get("transactions"))
        if volume < 0:
            errors.append(OptionsDayAggsNormalizationError(code="NEGATIVE_VOLUME", message="volume cannot be negative", row_number=row_number, field_name="volume"))
            continue
        if transactions < 0:
            errors.append(OptionsDayAggsNormalizationError(code="NEGATIVE_TRANSACTIONS", message="transactions cannot be negative", row_number=row_number, field_name="transactions"))
            continue
        _maybe_issue_warning(warnings, row_number=row_number, contract=contract, high_value=high_value, low_value=low_value)

        records.append(
            {
                "contract_symbol": contract.contract_symbol,
                "raw_ticker": contract.raw_ticker,
                "underlying_symbol": contract.underlying_symbol,
                "expiration_date": contract.expiration_date,
                "strike_price": contract.strike_price,
                "option_type": contract.option_type,
                "trade_date": row.get("trade_date"),
                "open": open_value,
                "high": high_value,
                "low": low_value,
                "close": close_value,
                "volume": volume,
                "transactions": transactions,
                "source": source,
                "source_dataset": source_dataset,
                "vendor": _vendor_from_source(parsed.source_file_path),
                "lineage": {
                    "source_file_path": parsed.source_file_path,
                    "source_file_sha256": parsed.source_file_sha256,
                    "row_number": row_number,
                    "vendor": _vendor_from_source(parsed.source_file_path),
                },
            }
        )

    normalization_status = "PASS" if not errors else "FAIL"
    return OptionsDayAggsNormalizationResult(
        normalization_status=normalization_status,
        records=tuple(records),
        record_count=len(records),
        warnings=tuple(warnings),
        errors=tuple(errors),
        source_file_sha256=parsed.source_file_sha256,
        source_file_path=parsed.source_file_path,
    )
