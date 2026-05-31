from __future__ import annotations

from dataclasses import dataclass

from app.normalization.common import safe_number, safe_text


@dataclass(frozen=True)
class NormalizedOptionsRecord:
    contract_symbol: str | None
    underlying_symbol: str | None
    expiration_date: str | None
    strike: float | None
    option_type: str | None
    bid: float | None
    ask: float | None
    last: float | None
    volume: float | None
    open_interest: float | None
    implied_volatility: float | None
    source: str | None
    notes: str | None


DEFAULT_FIXTURE_RECORDS: tuple[dict[str, object], ...] = (
    {
        "contract_symbol": "AAPL260619C00250000",
        "underlying_symbol": "AAPL",
        "expiration_date": "2026-06-19",
        "strike": 250.0,
        "option_type": "call",
        "bid": 11.2,
        "ask": 11.4,
        "last": 11.3,
        "volume": 15420,
        "open_interest": 84210,
        "implied_volatility": 0.24,
        "source": "manual_fixture",
        "notes": "deterministic fixture",
    },
    {
        "contract_symbol": "AAPL260619P00250000",
        "underlying_symbol": "AAPL",
        "expiration_date": "2026-06-19",
        "strike": 250.0,
        "option_type": "put",
        "bid": 8.6,
        "ask": 8.8,
        "last": 8.7,
        "volume": 9820,
        "open_interest": 63210,
        "implied_volatility": 0.27,
        "source": "manual_fixture",
        "notes": "deterministic fixture",
    },
    {
        "contract_symbol": "SPY260619C00550000",
        "underlying_symbol": "SPY",
        "expiration_date": "2026-06-19",
        "strike": 550.0,
        "option_type": "call",
        "bid": 10.1,
        "ask": 10.3,
        "last": 10.2,
        "volume": 24870,
        "open_interest": 112340,
        "implied_volatility": 0.18,
        "source": "manual_fixture",
        "notes": "deterministic fixture",
    },
    {
        "contract_symbol": "SPY260619P00550000",
        "underlying_symbol": "SPY",
        "expiration_date": "2026-06-19",
        "strike": 550.0,
        "option_type": "put",
        "bid": 9.4,
        "ask": 9.6,
        "last": 9.5,
        "volume": 22110,
        "open_interest": 98340,
        "implied_volatility": 0.19,
        "source": "manual_fixture",
        "notes": "deterministic fixture",
    },
)


def normalize_options_record(payload: dict[str, object]) -> NormalizedOptionsRecord:
    return NormalizedOptionsRecord(
        contract_symbol=safe_text(payload.get("contract_symbol")),
        underlying_symbol=safe_text(payload.get("underlying_symbol")),
        expiration_date=safe_text(payload.get("expiration_date")),
        strike=safe_number(payload.get("strike")),
        option_type=safe_text(payload.get("option_type")),
        bid=safe_number(payload.get("bid")),
        ask=safe_number(payload.get("ask")),
        last=safe_number(payload.get("last")),
        volume=safe_number(payload.get("volume")),
        open_interest=safe_number(payload.get("open_interest")),
        implied_volatility=safe_number(payload.get("implied_volatility")),
        source=safe_text(payload.get("source")),
        notes=safe_text(payload.get("notes")),
    )


def validate_options_record(record: NormalizedOptionsRecord) -> tuple[str, ...]:
    errors: list[str] = []
    if not record.contract_symbol:
        errors.append("contract_symbol is required")
    if not record.underlying_symbol:
        errors.append("underlying_symbol is required")
    if not record.expiration_date:
        errors.append("expiration_date is required")
    if record.strike is None:
        errors.append("strike is required")
    if not record.option_type:
        errors.append("option_type is required")
    if record.bid is None:
        errors.append("bid is required")
    if record.ask is None:
        errors.append("ask is required")
    if record.last is None:
        errors.append("last is required")
    if record.volume is None:
        errors.append("volume is required")
    if record.open_interest is None:
        errors.append("open_interest is required")
    if record.implied_volatility is None:
        errors.append("implied_volatility is required")
    if not record.source:
        errors.append("source is required")
    if not record.notes:
        errors.append("notes is required")
    return tuple(errors)
