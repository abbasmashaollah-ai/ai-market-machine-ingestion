from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable, Mapping

SECTOR_ETF_UNIVERSE = (
    "SPY",
    "XLB",
    "XLE",
    "XLF",
    "XLI",
    "XLK",
    "XLP",
    "XLRE",
    "XLU",
    "XLV",
    "XLY",
    "XLC",
)

REQUIRED_FIELDS = {
    "symbol",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "timeframe",
    "adjusted",
    "source",
    "dataset_version",
    "schema_version",
    "validation_status",
    "certification_status",
    "lineage_id",
    "source_file_sha256",
}

PRODUCTION_CANDIDATE_STATUSES = {"APPROVED_CANDIDATE", "PRODUCTION_CANDIDATE", "CERTIFIED"}
FIXTURE_ONLY_STATUSES = {"FIXTURE_ONLY"}


@dataclass(frozen=True, slots=True)
class AcceptanceDecision:
    symbol: str
    status: str
    reason: str | None = None
    idempotency_key_prefix: str | None = None


@dataclass(frozen=True, slots=True)
class SectorEtfOhlcvAcceptanceResult:
    records_received: int
    accepted_count: int
    rejected_count: int
    duplicate_count: int
    decisions: tuple[AcceptanceDecision, ...] = field(default_factory=tuple)
    symbols_accepted: tuple[str, ...] = field(default_factory=tuple)
    symbols_rejected: tuple[str, ...] = field(default_factory=tuple)
    validation_status: str = "PASS"
    production_write_attempted: bool = False
    db_write_attempted: bool = False
    vendor_call_attempted: bool = False
    scheduler_activation_attempted: bool = False
    idempotency_key_prefixes: tuple[str, ...] = field(default_factory=tuple)


def _normalize_symbol(value: object) -> str:
    return str(value).strip().upper()


def _required_timestamp(record: Mapping[str, object]) -> str | None:
    value = record.get("timestamp", record.get("observation_date"))
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value).strip() or None


def _idempotency_key_prefix(record: Mapping[str, object]) -> str:
    key = str(record.get("idempotency_key") or record.get("idempotency_key_prefix") or "")
    return key[:12]


def _validate_record(record: Mapping[str, object]) -> tuple[bool, str | None]:
    symbol = _normalize_symbol(record.get("symbol"))
    if symbol not in SECTOR_ETF_UNIVERSE:
        return False, f"invalid symbol: {symbol or '<missing>'}"

    missing = [field for field in REQUIRED_FIELDS if field not in record or record.get(field) in (None, "")]
    if missing:
        return False, f"missing required fields: {', '.join(sorted(missing))}"

    if _required_timestamp(record) is None:
        return False, "missing timestamp or observation_date"

    if not str(record.get("source_file_sha256") or "").strip():
        return False, "missing source_file_sha256"

    try:
        for field in ("open", "high", "low", "close", "volume"):
            if float(record.get(field)) <= 0:
                return False, f"invalid {field}"
    except (TypeError, ValueError):
        return False, "invalid numeric field"

    if str(record.get("validation_status")).strip().upper() != "PASS":
        return False, "validation_status must be PASS"

    cert_status = str(record.get("certification_status")).strip().upper()
    if cert_status in FIXTURE_ONLY_STATUSES:
        return False, "fixture-only records are rejected"
    if cert_status not in PRODUCTION_CANDIDATE_STATUSES:
        return False, "certification_status is not production-candidate"

    return True, None


def accept_sector_etf_ohlcv_handoff_records(
    records: Iterable[Mapping[str, object]],
    *,
    approved_candidate_test_mode: bool = False,
) -> SectorEtfOhlcvAcceptanceResult:
    seen: set[tuple[str, str, str, bool]] = set()
    decisions: list[AcceptanceDecision] = []
    accepted_symbols: list[str] = []
    rejected_symbols: list[str] = []
    idempotency_prefixes: list[str] = []
    accepted_count = 0
    rejected_count = 0
    duplicate_count = 0
    records_received = 0

    for record in records:
        records_received += 1
        symbol = _normalize_symbol(record.get("symbol"))
        key = (
            symbol,
            _required_timestamp(record) or "",
            str(record.get("timeframe") or ""),
            bool(record.get("adjusted")),
        )
        prefix = _idempotency_key_prefix(record)
        idempotency_prefixes.append(prefix)

        if key in seen:
            duplicate_count += 1
            decisions.append(AcceptanceDecision(symbol=symbol, status="DUPLICATE", reason="duplicate canonical key", idempotency_key_prefix=prefix))
            continue
        seen.add(key)

        valid, reason = _validate_record(record)
        if not valid:
            rejected_count += 1
            rejected_symbols.append(symbol)
            decisions.append(AcceptanceDecision(symbol=symbol, status="REJECTED", reason=reason, idempotency_key_prefix=prefix))
            continue

        if approved_candidate_test_mode:
            accepted_count += 1
            accepted_symbols.append(symbol)
            decisions.append(AcceptanceDecision(symbol=symbol, status="ACCEPTED", reason="approved candidate dry-run", idempotency_key_prefix=prefix))
        else:
            # Safe default: the service only proves the acceptance decision boundary.
            accepted_count += 1
            accepted_symbols.append(symbol)
            decisions.append(AcceptanceDecision(symbol=symbol, status="ACCEPTED", reason="accepted in dry-run decision form", idempotency_key_prefix=prefix))

    validation_status = "PASS" if rejected_count == 0 else "FAIL"
    return SectorEtfOhlcvAcceptanceResult(
        records_received=records_received,
        accepted_count=accepted_count,
        rejected_count=rejected_count,
        duplicate_count=duplicate_count,
        decisions=tuple(decisions),
        symbols_accepted=tuple(accepted_symbols),
        symbols_rejected=tuple(rejected_symbols),
        validation_status=validation_status,
        idempotency_key_prefixes=tuple(idempotency_prefixes),
    )
