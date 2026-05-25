from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from app.ingestion.ohlcv.normalization import normalize_fmp_ohlcv_records
from app.models.normalized import NormalizedOHLCVRecord
from app.state.checkpoints import CheckpointStatus, IngestionCheckpoint
from app.vendors.fmp.client import FmpClientConfig, FmpFetchError, UnsupportedFmpClient, build_fmp_client


@dataclass(frozen=True)
class FmpOhlcvIngestionRequest:
    symbol: str
    start_date: date
    end_date: date
    api_key: str | None = None
    timeframe: str = "1d"


@dataclass(frozen=True)
class FmpOhlcvIngestionPlan:
    vendor: str
    symbol: str
    timeframe: str
    requested_start_date: date
    requested_end_date: date
    raw_record_count: int
    normalized_record_count: int
    did_write_db: bool
    intended_target: str
    write_mode: str
    normalized_records: tuple[NormalizedOHLCVRecord, ...] = ()
    lineage_evidence: dict[str, object] = field(default_factory=dict)
    checkpoint_plan: dict[str, object] = field(default_factory=dict)
    writer_handoff_ready: bool = False
    intended_writer_target: str = "canonical_ohlcv"
    writer_payload_preview: dict[str, object] = field(default_factory=dict)
    errors: tuple[dict[str, object], ...] = field(default_factory=tuple)
    status: str = "completed"


def _build_checkpoint_plan(request: FmpOhlcvIngestionRequest) -> dict[str, object]:
    checkpoint_id = f"fmp:ohlcv:{request.symbol}:{request.timeframe}:{request.start_date.isoformat()}:{request.end_date.isoformat()}"
    checkpoint = IngestionCheckpoint(
        checkpoint_id=checkpoint_id,
        job_id=checkpoint_id,
        last_successful_date=None,
        attempt_count=0,
        status=CheckpointStatus.PENDING,
        metadata={
            "checkpoint_persistence": "not_implemented",
            "resume_supported": False,
            "update_supported": False,
            "owner": "ai-market-machine-ingestion",
        },
    )
    return {
        "checkpoint_id": checkpoint.checkpoint_id,
        "job_id": checkpoint.job_id,
        "status": checkpoint.status,
        "last_successful_date": checkpoint.last_successful_date,
        "attempt_count": checkpoint.attempt_count,
        "metadata": checkpoint.metadata,
    }


def _build_lineage_evidence(
    *,
    request: FmpOhlcvIngestionRequest,
    normalized_record_count: int,
    did_write_db: bool,
) -> dict[str, object]:
    return {
        "vendor": "fmp",
        "dataset": "ohlcv",
        "symbol": request.symbol,
        "timeframe": request.timeframe,
        "source_endpoint": f"/api/v3/historical-price-full/{request.symbol}",
        "request_params": {
            "from": request.start_date.isoformat(),
            "to": request.end_date.isoformat(),
        },
        "row_count": normalized_record_count,
        "normalization_version": "fmp.ohlcv.v1",
        "quality_status": "pending",
        "intended_target": "canonical_ohlcv",
        "write_mode": "dry_run",
        "did_write_db": did_write_db,
    }


def _required_writer_fields(record: NormalizedOHLCVRecord) -> dict[str, object]:
    missing: list[str] = []
    symbol = record.symbol or record.symbol_id
    if symbol is None:
        missing.append("symbol")
    if record.timestamp is None:
        missing.append("timestamp")
    for field_name, field_value in (
        ("open", record.open),
        ("high", record.high),
        ("low", record.low),
        ("close", record.close),
        ("volume", record.volume),
        ("source", record.source),
        ("timeframe", record.timeframe),
    ):
        if field_value is None or field_value == "":
            missing.append(field_name)
    if record.adjusted is None:
        missing.append("adjusted")
    if record.quality_status is None:
        missing.append("data_quality_status")
    if missing:
        raise ValueError(f"normalized OHLCV record is missing writer-required fields: {', '.join(sorted(set(missing)))}")
    return {
        "symbol": symbol,
        "timestamp": record.timestamp,
        "open": record.open,
        "high": record.high,
        "low": record.low,
        "close": record.close,
        "volume": record.volume,
        "source": record.source,
        "adjustment_status": "adjusted" if record.adjusted else "unadjusted",
        "data_quality_status": record.quality_status or "pending",
        "timeframe": record.timeframe,
        "adjusted": record.adjusted,
    }


def _build_writer_payload_preview(records: tuple[NormalizedOHLCVRecord, ...]) -> dict[str, object]:
    return {
        "writer_name": "ohlcv_writer",
        "target_table": "canonical_ohlcv",
        "record_count": len(records),
        "records": tuple(_required_writer_fields(record) for record in records),
        "handoff_ready": bool(records),
    }


def _build_fmp_client(request: FmpOhlcvIngestionRequest) -> UnsupportedFmpClient:
    return build_fmp_client(FmpClientConfig(api_key=request.api_key))


def build_single_symbol_ohlcv_write_plan(
    request: FmpOhlcvIngestionRequest,
    *,
    client: UnsupportedFmpClient | None = None,
) -> FmpOhlcvIngestionPlan:
    fmp_client = client or _build_fmp_client(request)
    errors: list[dict[str, object]] = []
    raw_records: list[dict[str, object]] = []
    normalized_records: tuple[NormalizedOHLCVRecord, ...] = ()
    try:
        raw_records = fmp_client.fetch_historical_ohlcv_raw(
            request.symbol,
            start_date=request.start_date.isoformat(),
            end_date=request.end_date.isoformat(),
        )
        normalized_records = normalize_fmp_ohlcv_records(raw_records, symbol=request.symbol)
        normalized_records = _dedupe_normalized_records(normalized_records)
    except FmpFetchError as exc:
        errors.append(
            {
                "kind": exc.kind.value,
                "message": exc.message,
                "retryable": exc.retryable,
                "source": "vendor_fetch",
            }
        )
    except Exception as exc:
        errors.append(
            {
                "kind": "unexpected",
                "message": str(exc),
                "retryable": False,
                "source": "orchestrator",
            }
        )
    lineage_evidence = _build_lineage_evidence(
        request=request,
        normalized_record_count=len(normalized_records),
        did_write_db=False,
    )
    checkpoint_plan = _build_checkpoint_plan(request)
    writer_payload_preview = _build_writer_payload_preview(normalized_records)
    status = "failed" if errors else "completed"
    return FmpOhlcvIngestionPlan(
        vendor="fmp",
        symbol=request.symbol,
        timeframe=request.timeframe,
        requested_start_date=request.start_date,
        requested_end_date=request.end_date,
        raw_record_count=len(raw_records),
        normalized_record_count=len(normalized_records),
        did_write_db=False,
        intended_target="canonical_ohlcv",
        write_mode="dry_run",
        normalized_records=normalized_records,
        lineage_evidence=lineage_evidence,
        checkpoint_plan=checkpoint_plan,
        writer_handoff_ready=bool(normalized_records) and not errors,
        intended_writer_target="canonical_ohlcv",
        writer_payload_preview=writer_payload_preview,
        errors=tuple(errors),
        status=status,
    )


def _dedupe_normalized_records(records: tuple[NormalizedOHLCVRecord, ...]) -> tuple[NormalizedOHLCVRecord, ...]:
    seen: set[tuple[object, ...]] = set()
    unique: list[NormalizedOHLCVRecord] = []
    for record in records:
        key = (record.symbol or record.symbol_id, record.timestamp, record.timeframe, record.adjusted)
        if key in seen:
            continue
        seen.add(key)
        unique.append(record)
    return tuple(unique)
