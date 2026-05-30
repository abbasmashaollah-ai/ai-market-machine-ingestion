from __future__ import annotations

from dataclasses import dataclass

from app.normalization.common import safe_date, safe_text


RECORD_FAMILIES = (
    "company_profile",
    "financial_statement",
    "financial_metric",
    "earnings_estimate",
    "sec_filing",
)


@dataclass(frozen=True)
class NormalizedFundamentalsFilingsRecord:
    record_family: str | None
    symbol: str | None
    source: str | None
    record_date: str | None
    period: str | None
    payload: dict[str, object] | None
    notes: str | None


DEFAULT_FIXTURE_RECORDS: tuple[dict[str, object], ...] = (
    {
        "record_family": "company_profile",
        "symbol": "AAPL",
        "source": "manual_fixture",
        "record_date": "2026-05-30",
        "period": "ttm",
        "payload": {"company_name": "Apple Inc.", "exchange": "NASDAQ", "sector": "Technology"},
        "notes": "deterministic fixture",
    },
    {
        "record_family": "financial_statement",
        "symbol": "MSFT",
        "source": "manual_fixture",
        "record_date": "2026-05-30",
        "period": "FY2026-Q2",
        "payload": {"statement_type": "income_statement", "revenue": 100.0, "net_income": 42.0},
        "notes": "deterministic fixture",
    },
    {
        "record_family": "financial_metric",
        "symbol": "NVDA",
        "source": "manual_fixture",
        "record_date": "2026-05-30",
        "period": "ttm",
        "payload": {"metric_name": "gross_margin", "value": 0.74},
        "notes": "deterministic fixture",
    },
    {
        "record_family": "earnings_estimate",
        "symbol": "AAPL",
        "source": "manual_fixture",
        "record_date": "2026-05-30",
        "period": "FY2026",
        "payload": {"estimate_type": "eps", "mean": 6.12, "high": 6.5, "low": 5.8},
        "notes": "deterministic fixture",
    },
    {
        "record_family": "sec_filing",
        "symbol": "MSFT",
        "source": "manual_fixture",
        "record_date": "2026-05-30",
        "period": "10-K",
        "payload": {"accession": "0000789019-26-000001", "form_type": "10-K", "filing_url": "https://www.sec.gov/"},
        "notes": "deterministic fixture",
    },
)


def normalize_fundamentals_filings_record(payload: dict[str, object]) -> NormalizedFundamentalsFilingsRecord:
    return NormalizedFundamentalsFilingsRecord(
        record_family=safe_text(payload.get("record_family")),
        symbol=safe_text(payload.get("symbol")),
        source=safe_text(payload.get("source")),
        record_date=safe_text(safe_date(payload.get("record_date"))),
        period=safe_text(payload.get("period")),
        payload=payload.get("payload") if isinstance(payload.get("payload"), dict) else None,
        notes=safe_text(payload.get("notes")),
    )


def validate_fundamentals_filings_record(record: NormalizedFundamentalsFilingsRecord) -> tuple[str, ...]:
    errors: list[str] = []
    if not record.record_family:
        errors.append("record_family is required")
    elif record.record_family not in RECORD_FAMILIES:
        errors.append("record_family is invalid")
    if not record.symbol:
        errors.append("symbol is required")
    if not record.source:
        errors.append("source is required")
    if not record.record_date:
        errors.append("record_date is required")
    if not record.period:
        errors.append("period is required")
    if record.payload is None:
        errors.append("payload is required")
    if not record.notes:
        errors.append("notes is required")
    return tuple(errors)
