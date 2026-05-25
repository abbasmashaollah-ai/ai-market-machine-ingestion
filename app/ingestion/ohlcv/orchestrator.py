from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from app.ingestion.ohlcv.normalization import normalize_fmp_ohlcv_records
from app.models.normalized import NormalizedOHLCVRecord
from app.state.checkpoints import CheckpointStatus, IngestionCheckpoint
from app.writers.canonical_writer import WriteStatus, WriterResult
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
    writer_execution_requested: bool = False
    writer_execution_performed: bool = False
    writer_handoff_ready: bool = False
    intended_writer_target: str = "canonical_ohlcv"
    writer_payload_preview: dict[str, object] = field(default_factory=dict)
    writer_result: dict[str, object] | None = None
    writer_errors: tuple[dict[str, object], ...] = field(default_factory=tuple)
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


def _writer_result_to_dict(result: WriterResult) -> dict[str, object]:
    return {
        "writer_name": result.writer_name,
        "status": result.status.value,
        "written_count": result.written_count,
        "skipped_count": result.skipped_count,
        "failed_count": result.failed_count,
        "message": result.message,
        "details": dict(result.details),
        "succeeded": result.succeeded,
    }


def _build_fmp_client(request: FmpOhlcvIngestionRequest) -> UnsupportedFmpClient:
    return build_fmp_client(FmpClientConfig(api_key=request.api_key))


def build_single_symbol_ohlcv_write_plan(
    request: FmpOhlcvIngestionRequest,
    *,
    client: UnsupportedFmpClient | None = None,
    writer: object | None = None,
    execute_writer: bool = False,
) -> FmpOhlcvIngestionPlan:
    fmp_client = client or _build_fmp_client(request)
    errors: list[dict[str, object]] = []
    writer_errors: list[dict[str, object]] = []
    raw_records: list[dict[str, object]] = []
    normalized_records: tuple[NormalizedOHLCVRecord, ...] = ()
    writer_result: dict[str, object] | None = None
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
    writer_execution_requested = bool(execute_writer)
    writer_execution_performed = False
    did_write_db = False
    if writer_execution_requested and not errors:
        try:
            if writer is None:
                raise ValueError("writer execution was requested but no writer was provided")
            writer_execution_performed = True
            result = writer.write(list(writer_payload_preview["records"]))  # type: ignore[call-arg]
            if not isinstance(result, WriterResult):
                raise TypeError("writer did not return a WriterResult")
            writer_result = _writer_result_to_dict(result)
            if result.status == WriteStatus.SUCCESS:
                did_write_db = True
            else:
                writer_errors.append(
                    {
                        "kind": "writer_failure",
                        "message": result.message or "writer returned failure",
                        "writer_name": result.writer_name,
                        "status": result.status.value,
                        "details": dict(result.details),
                    }
                )
        except Exception as exc:
            writer_errors.append(
                {
                    "kind": "writer_error",
                    "message": str(exc),
                    "retryable": False,
                    "source": "writer_execution",
                }
            )
    if not writer_execution_requested or not writer_execution_performed:
        did_write_db = False
    lineage_evidence = _build_lineage_evidence(
        request=request,
        normalized_record_count=len(normalized_records),
        did_write_db=did_write_db,
    )
    if did_write_db:
        lineage_evidence["write_mode"] = "write"
    status = "failed" if errors or writer_errors else "completed"
    return FmpOhlcvIngestionPlan(
        vendor="fmp",
        symbol=request.symbol,
        timeframe=request.timeframe,
        requested_start_date=request.start_date,
        requested_end_date=request.end_date,
        raw_record_count=len(raw_records),
        normalized_record_count=len(normalized_records),
        did_write_db=did_write_db,
        intended_target="canonical_ohlcv",
        write_mode="dry_run",
        normalized_records=normalized_records,
        lineage_evidence=lineage_evidence,
        checkpoint_plan=checkpoint_plan,
        writer_execution_requested=writer_execution_requested,
        writer_execution_performed=writer_execution_performed,
        writer_handoff_ready=bool(normalized_records) and not errors,
        intended_writer_target="canonical_ohlcv",
        writer_payload_preview=writer_payload_preview,
        writer_result=writer_result,
        writer_errors=tuple(writer_errors),
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
