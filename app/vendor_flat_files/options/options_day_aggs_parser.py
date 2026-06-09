from __future__ import annotations

import csv
import gzip
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

REQUIRED_COLUMNS = ("ticker", "volume", "open", "close", "high", "low", "window_start", "transactions")


@dataclass(frozen=True, slots=True)
class OptionsDayAggsParseError:
    code: str
    message: str
    row_number: int | None = None
    field_name: str | None = None


@dataclass(frozen=True, slots=True)
class OptionsDayAggsParseResult:
    parse_status: str
    rows: tuple[dict[str, object], ...] = field(default_factory=tuple)
    row_count: int = 0
    header_columns: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    errors: tuple[OptionsDayAggsParseError, ...] = field(default_factory=tuple)
    source_file_sha256: str | None = None
    source_file_path: str | None = None


@dataclass(frozen=True, slots=True)
class ParsedOptionsContract:
    contract_symbol: str
    raw_ticker: str
    underlying_symbol: str | None
    expiration_date: str | None
    strike_price: Decimal | None
    option_type: str | None
    parse_ok: bool
    warning: str | None = None


def _sha256(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalize_decimal(value: object) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"invalid decimal: {value!r}") from exc


def parse_opra_option_symbol(symbol: str) -> ParsedOptionsContract:
    raw = str(symbol or "")
    working = raw[2:] if raw.startswith("O:") else raw
    if len(working) < 15:
        return ParsedOptionsContract(raw, raw, None, None, None, None, False, "symbol too short")
    underlying = working[:-15]
    tail = working[-15:]
    yymmdd = tail[:6]
    option_type = tail[6:7]
    strike_raw = tail[7:]
    if not underlying or option_type not in {"C", "P"} or not yymmdd.isdigit() or not strike_raw.isdigit():
        return ParsedOptionsContract(raw, raw, None, None, None, None, False, "symbol format not recognized")
    try:
        expiration = datetime.strptime(yymmdd, "%y%m%d").date().isoformat()
        strike = Decimal(str(int(strike_raw))) / Decimal(1000)
    except Exception:
        return ParsedOptionsContract(raw, raw, None, None, None, None, False, "symbol parse failed")
    return ParsedOptionsContract(raw, raw, underlying, expiration, strike, option_type, True, None)


def _parse_trade_date(window_start: object) -> str | None:
    value = str(window_start or "").strip()
    if not value:
        return None
    if len(value) == 10:
        try:
            return date.fromisoformat(value).isoformat()
        except ValueError:
            return None
    if not value.isdigit():
        return None
    try:
        numeric = int(value)
    except ValueError:
        return None
    if numeric >= 10**18:
        seconds = numeric / 1_000_000_000
    elif numeric >= 10**15:
        seconds = numeric / 1_000_000
    else:
        seconds = float(numeric)
    return datetime.fromtimestamp(seconds, tz=timezone.utc).date().isoformat()


def _trade_date_from_window_start(window_start: str) -> str | None:
    return _parse_trade_date(window_start)


def _validate_header(header: list[str]) -> list[OptionsDayAggsParseError]:
    errors: list[OptionsDayAggsParseError] = []
    if tuple(header) != REQUIRED_COLUMNS:
        errors.append(
            OptionsDayAggsParseError(
                code="REQUIRED_HEADER_MISMATCH",
                message="required header columns mismatch",
            )
    )
    return errors


def _stream_parsed_rows(handle: object) -> tuple[list[dict[str, object]], list[OptionsDayAggsParseError], list[str]]:
    reader = csv.DictReader(handle)
    header = list(reader.fieldnames or [])
    errors = _validate_header(header)
    warnings: list[str] = []
    parsed_rows: list[dict[str, object]] = []
    if errors:
        return parsed_rows, errors, warnings
    for row_number, row in enumerate(reader, start=2):
        ticker = str(row.get("ticker") or "").strip()
        if not ticker:
            errors.append(
                OptionsDayAggsParseError(
                    code="REQUIRED_VALUE_MISSING",
                    message="ticker missing",
                    row_number=row_number,
                    field_name="ticker",
                )
            )
            continue
        try:
            volume = int(str(row.get("volume") or "").strip())
            transactions = int(str(row.get("transactions") or "").strip())
            open_value = _normalize_decimal(row.get("open"))
            close_value = _normalize_decimal(row.get("close"))
            high_value = _normalize_decimal(row.get("high"))
            low_value = _normalize_decimal(row.get("low"))
        except Exception as exc:
            errors.append(
                OptionsDayAggsParseError(
                    code="NUMERIC_PARSE_FAILED",
                    message=str(exc),
                    row_number=row_number,
                )
            )
            continue
        window_start = str(row.get("window_start") or "").strip()
        trade_date = _parse_trade_date(window_start)
        if window_start and trade_date is None:
            warnings.append(f"row {row_number}: unable to derive trade_date from window_start")
        parsed_rows.append(
            {
                "row_number": row_number,
                "ticker": ticker,
                "volume": volume,
                "transactions": transactions,
                "open": open_value,
                "close": close_value,
                "high": high_value,
                "low": low_value,
                "window_start": window_start,
                "trade_date": trade_date,
            }
        )
    return parsed_rows, errors, warnings


def parse_options_day_aggs_quarantine_file(*, input_path: str | Path, source_file_sha256: str | None = None) -> OptionsDayAggsParseResult:
    path = Path(input_path)
    if source_file_sha256 is None and path.exists():
        source_file_sha256 = _sha256(path)
    if not path.exists():
        return OptionsDayAggsParseResult(
            parse_status="FAIL",
            errors=(OptionsDayAggsParseError(code="INPUT_MISSING", message="input file missing"),),
            source_file_sha256=source_file_sha256,
            source_file_path=str(path),
        )

    try:
        with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
            parsed_rows, errors, warnings = _stream_parsed_rows(handle)
    except Exception as exc:
        errors = [OptionsDayAggsParseError(code="GZIP_OR_CSV_ERROR", message=exc.__class__.__name__)]
        return OptionsDayAggsParseResult(
            parse_status="FAIL",
            errors=tuple(errors),
            source_file_sha256=source_file_sha256,
            source_file_path=str(path),
        )

    parse_status = "PASS" if not errors else "FAIL"
    return OptionsDayAggsParseResult(
        parse_status=parse_status,
        rows=tuple(parsed_rows),
        row_count=len(parsed_rows),
        header_columns=tuple(REQUIRED_COLUMNS),
        warnings=tuple(warnings),
        errors=tuple(errors),
        source_file_sha256=source_file_sha256,
        source_file_path=str(path),
    )
