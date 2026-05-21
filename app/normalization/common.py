from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation


def safe_text(value: object, default: str | None = None) -> str | None:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def safe_bool(value: object, default: bool | None = None) -> bool | None:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in (0, 1):
        return bool(value)
    text = str(value).strip().lower()
    if text in {"true", "t", "yes", "y", "1"}:
        return True
    if text in {"false", "f", "no", "n", "0"}:
        return False
    return default


def safe_decimal(value: object, default: Decimal | None = None) -> Decimal | None:
    if value is None:
        return default
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return default


def safe_number(value: object, default: float | None = None) -> float | None:
    decimal_value = safe_decimal(value)
    if decimal_value is None:
        return default
    return float(decimal_value)


def safe_date(value: object, default: date | None = None) -> date | None:
    if value is None:
        return default
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    text = str(value).strip()
    if not text:
        return default
    try:
        return date.fromisoformat(text)
    except ValueError:
        return default


def safe_datetime(value: object, default: datetime | None = None) -> datetime | None:
    if value is None:
        return default
    if isinstance(value, datetime):
        dt = value
    else:
        text = str(value).strip()
        if not text:
            return default
        normalized = text.replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(normalized)
        except ValueError:
            return default
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


@dataclass(frozen=True)
class FieldMap:
    key: str
    alternate_keys: tuple[str, ...] = ()

    def extract(self, payload: dict[str, object]) -> object | None:
        if self.key in payload:
            return payload[self.key]
        for alternate_key in self.alternate_keys:
            if alternate_key in payload:
                return payload[alternate_key]
        return None
