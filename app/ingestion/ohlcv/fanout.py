from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Protocol

from app.ingestion.ohlcv.orchestrator import (
    FmpOhlcvIngestionPlan,
    FmpOhlcvIngestionRequest,
    build_single_symbol_ohlcv_write_plan,
)
from app.vendors.fmp.client import UnsupportedFmpClient


@dataclass(frozen=True)
class FmpMultiSymbolOhlcvFanoutRequest:
    symbols: tuple[str, ...]
    start_date: date
    end_date: date
    api_key: str | None = None
    timeframe: str = "1d"


@dataclass(frozen=True)
class FmpMultiSymbolOhlcvFanoutResult:
    vendor: str
    timeframe: str
    requested_start_date: date
    requested_end_date: date
    requested_symbols: tuple[str, ...]
    completed_symbols: tuple[str, ...]
    failed_symbols: tuple[str, ...]
    per_symbol_results: tuple[dict[str, object], ...]
    raw_record_count: int
    normalized_record_count: int
    writer_status: str
    checkpoint_status: str
    batch_errors: tuple[dict[str, object], ...] = field(default_factory=tuple)
    did_write_db: bool = False
    fail_fast: bool = False


class _SymbolPlanProtocol(Protocol):
    def __call__(self, request: FmpOhlcvIngestionRequest, **kwargs: object) -> FmpOhlcvIngestionPlan:
        ...


def _plan_to_dict(plan: FmpOhlcvIngestionPlan) -> dict[str, object]:
    return {
        "vendor": plan.vendor,
        "symbol": plan.symbol,
        "timeframe": plan.timeframe,
        "requested_start_date": plan.requested_start_date.isoformat(),
        "requested_end_date": plan.requested_end_date.isoformat(),
        "raw_record_count": plan.raw_record_count,
        "normalized_record_count": plan.normalized_record_count,
        "did_write_db": plan.did_write_db,
        "intended_target": plan.intended_target,
        "write_mode": plan.write_mode,
        "checkpoint_persistence_requested": plan.checkpoint_persistence_requested,
        "checkpoint_persistence_performed": plan.checkpoint_persistence_performed,
        "checkpoint_result": plan.checkpoint_result,
        "checkpoint_errors": plan.checkpoint_errors,
        "writer_execution_requested": plan.writer_execution_requested,
        "writer_execution_performed": plan.writer_execution_performed,
        "writer_handoff_ready": plan.writer_handoff_ready,
        "intended_writer_target": plan.intended_writer_target,
        "writer_payload_preview": plan.writer_payload_preview,
        "writer_result": plan.writer_result,
        "writer_errors": plan.writer_errors,
        "errors": plan.errors,
        "status": plan.status,
    }


def build_multi_symbol_ohlcv_fanout(
    request: FmpMultiSymbolOhlcvFanoutRequest,
    *,
    client: UnsupportedFmpClient | None = None,
    symbol_orchestrator: _SymbolPlanProtocol = build_single_symbol_ohlcv_write_plan,
    writer: object | None = None,
    execute_writer: bool = False,
    checkpoint_writer: object | None = None,
    execute_checkpoint_persistence: bool = False,
    fail_fast: bool = False,
) -> FmpMultiSymbolOhlcvFanoutResult:
    per_symbol_results: list[dict[str, object]] = []
    completed_symbols: list[str] = []
    failed_symbols: list[str] = []
    batch_errors: list[dict[str, object]] = []
    total_raw = 0
    total_normalized = 0
    did_write_db = False
    writer_status = "not_requested"
    checkpoint_status = "not_requested"

    for symbol in request.symbols:
        symbol_request = FmpOhlcvIngestionRequest(
            symbol=symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            api_key=request.api_key,
            timeframe=request.timeframe,
        )
        try:
            plan = symbol_orchestrator(
                symbol_request,
                client=client,
                writer=writer if execute_writer else None,
                execute_writer=execute_writer,
                checkpoint_writer=checkpoint_writer if execute_checkpoint_persistence else None,
                execute_checkpoint_persistence=execute_checkpoint_persistence,
            )
            plan_dict = _plan_to_dict(plan)
            per_symbol_results.append(plan_dict)
            total_raw += plan.raw_record_count
            total_normalized += plan.normalized_record_count
            did_write_db = did_write_db or plan.did_write_db
            if plan.writer_execution_performed:
                writer_status = "failed" if plan.writer_errors else "completed"
            if plan.checkpoint_persistence_performed:
                checkpoint_status = "failed" if plan.checkpoint_errors else "completed"
            if plan.status == "failed":
                failed_symbols.append(symbol)
                if fail_fast:
                    break
            else:
                completed_symbols.append(symbol)
        except Exception as exc:
            failed_symbols.append(symbol)
            batch_errors.append(
                {
                    "kind": "symbol_orchestrator_error",
                    "symbol": symbol,
                    "message": str(exc),
                    "retryable": False,
                }
            )
            per_symbol_results.append(
                {
                    "vendor": "fmp",
                    "symbol": symbol,
                    "timeframe": request.timeframe,
                    "requested_start_date": request.start_date.isoformat(),
                    "requested_end_date": request.end_date.isoformat(),
                    "raw_record_count": 0,
                    "normalized_record_count": 0,
                    "did_write_db": False,
                    "intended_target": "canonical_ohlcv",
                    "write_mode": "dry_run",
                    "checkpoint_persistence_requested": execute_checkpoint_persistence,
                    "checkpoint_persistence_performed": False,
                    "checkpoint_result": None,
                    "checkpoint_errors": (),
                    "writer_execution_requested": execute_writer,
                    "writer_execution_performed": False,
                    "writer_handoff_ready": False,
                    "intended_writer_target": "canonical_ohlcv",
                    "writer_payload_preview": {},
                    "writer_result": None,
                    "writer_errors": (),
                    "errors": tuple(batch_errors[-1:]),
                    "status": "failed",
                }
            )
            if fail_fast:
                break

    return FmpMultiSymbolOhlcvFanoutResult(
        vendor="fmp",
        timeframe=request.timeframe,
        requested_start_date=request.start_date,
        requested_end_date=request.end_date,
        requested_symbols=request.symbols,
        completed_symbols=tuple(completed_symbols),
        failed_symbols=tuple(failed_symbols),
        per_symbol_results=tuple(per_symbol_results),
        raw_record_count=total_raw,
        normalized_record_count=total_normalized,
        writer_status=writer_status,
        checkpoint_status=checkpoint_status,
        batch_errors=tuple(batch_errors),
        did_write_db=did_write_db,
        fail_fast=fail_fast,
    )
