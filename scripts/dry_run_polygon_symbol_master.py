from __future__ import annotations

import argparse
from dataclasses import dataclass
import os
from contextlib import closing
from datetime import datetime, timezone
from typing import Any

from app.normalization.symbol_master import validate_symbol_record
from app.quality.validators import ValidationResult, ValidationSeverity, ValidationStatus
from app.state.data_lineage_store import DataLineageStore
from app.state.data_quality_result_store import DataQualityResultStore
from app.state.ingestion_run_store import IngestionRunStore
from app.state.runs import IngestionRun, RunStatus
from app.vendors.polygon_symbol_master import PolygonSymbolMasterAdapter, PolygonSymbolMasterSourceConfig
from app.writers.symbol_master_writer import SymbolMasterWriter


@dataclass(frozen=True)
class _RecordingStores:
    run_store: IngestionRunStore | None = None
    quality_store: DataQualityResultStore | None = None
    lineage_store: DataLineageStore | None = None


def _load_postgres_connect():
    try:
        from psycopg import connect as psycopg_connect  # type: ignore
    except ImportError:
        try:
            from psycopg2 import connect as psycopg_connect  # type: ignore
        except ImportError as exc:  # pragma: no cover - dependency specific
            raise RuntimeError("symbol master confirmed writes require psycopg or psycopg2.") from exc
    return psycopg_connect


def _open_connection(database_url: str):
    scheme = database_url.split(":", 1)[0].lower()
    if scheme not in {"postgresql", "postgres"}:
        raise RuntimeError("symbol master confirmed writes require a postgres DATABASE_URL")
    return _load_postgres_connect()(database_url)


def _emit(summary: dict[str, object]) -> None:
    for key in (
        "input_count",
        "normalized_count",
        "valid_count",
        "invalid_count",
        "rows_written",
        "rows_skipped",
        "write_confirmed",
        "vendor",
        "dry_run",
    ):
        print(f"{key}={summary.get(key)}")


def _build_adapter(*, live_check: bool) -> PolygonSymbolMasterAdapter:
    return PolygonSymbolMasterAdapter(
        PolygonSymbolMasterSourceConfig(api_key=os.getenv("POLYGON_API_KEY") if live_check else None)
    )


def _build_records(*, live_check: bool) -> tuple[list[object], PolygonSymbolMasterAdapter]:
    adapter = _build_adapter(live_check=live_check)
    payloads = adapter.fetch_reference_tickers_raw() if live_check else adapter.build_sample_reference_payloads()
    records = [adapter.map_reference_ticker(payload) for payload in payloads]
    return records, adapter


def _require_recording_contract(confirm_write: bool, live_check: bool) -> None:
    if not confirm_write or not live_check:
        raise RuntimeError("Polygon symbol-master recording requires --live-check and --confirm-write")


def _build_run(*, run_id: str, count: int, valid_count: int, invalid_count: int, write_confirmed: bool) -> IngestionRun:
    status = RunStatus.SUCCESS if invalid_count == 0 and write_confirmed else RunStatus.PARTIAL if valid_count > 0 else RunStatus.FAILED
    return IngestionRun(
        run_id=run_id,
        job_id="manual_polygon_symbol_master",
        status=status,
        rows_fetched=count,
        rows_written=valid_count if write_confirmed else 0,
        rows_rejected=invalid_count,
        error_count=invalid_count,
        metadata={
            "vendor": "polygon",
            "dataset": "symbol_master",
            "started_at": datetime.now(timezone.utc),
            "finished_at": datetime.now(timezone.utc),
            "confirmed_write": write_confirmed,
            "dry_run": not write_confirmed,
        },
    )


def _quality_results(*, valid_count: int, invalid_count: int, write_confirmed: bool) -> list[ValidationResult]:
    status = ValidationStatus.PASS if invalid_count == 0 and write_confirmed else ValidationStatus.WARN if valid_count > 0 else ValidationStatus.FAIL
    severity = ValidationSeverity.INFO if status == ValidationStatus.PASS else ValidationSeverity.WARN if status == ValidationStatus.WARN else ValidationSeverity.ERROR
    return [
        ValidationResult(
            check_name="polygon_symbol_master_summary",
            status=status,
            severity=severity,
            message="polygon symbol master summary",
            details={"observed_value": valid_count, "expected_value": valid_count + invalid_count, "write_confirmed": write_confirmed},
        )
    ]


def _lineage_payload(*, valid_count: int, invalid_count: int, write_confirmed: bool) -> dict[str, object]:
    return {
        "vendor": "polygon",
        "dataset": "symbol_master",
        "symbol": None,
        "timeframe": None,
        "source_endpoint": "/v3/reference/tickers",
        "request_params": None,
        "response_status": 200 if write_confirmed else 204,
        "row_count": valid_count + invalid_count,
        "normalization_version": "polygon.symbol_master.v1",
        "quality_status": "pass" if invalid_count == 0 and write_confirmed else "warn" if valid_count > 0 else "fail",
        "run_id": None,
        "job_id": "manual_polygon_symbol_master",
    }


def _record_optional_evidence(*, stores: _RecordingStores, run_id: str, valid_count: int, invalid_count: int, write_confirmed: bool) -> None:
    if stores.run_store is not None:
        stores.run_store.save_run(_build_run(run_id=run_id, count=valid_count + invalid_count, valid_count=valid_count, invalid_count=invalid_count, write_confirmed=write_confirmed))
    if stores.quality_store is not None:
        stores.quality_store.save_validation_results(
            vendor="polygon",
            dataset="symbol_master",
            symbol=None,
            timeframe=None,
            results=_quality_results(valid_count=valid_count, invalid_count=invalid_count, write_confirmed=write_confirmed),
            run_id=run_id,
            job_id=None,
        )
    if stores.lineage_store is not None:
        payload = _lineage_payload(valid_count=valid_count, invalid_count=invalid_count, write_confirmed=write_confirmed)
        stores.lineage_store.save_chunk_lineage(**payload)


def build_summary(*, live_check: bool, confirm_write: bool, record_run: bool, record_quality: bool, record_lineage: bool) -> dict[str, object]:
    records, _ = _build_records(live_check=live_check)
    valid_records = [record for record in records if not validate_symbol_record(record)]
    summary: dict[str, object] = {
        "vendor": "polygon",
        "dry_run": not confirm_write,
        "input_count": len(records),
        "normalized_count": len(records),
        "valid_count": len(valid_records),
        "invalid_count": len(records) - len(valid_records),
        "rows_written": 0,
        "rows_skipped": 0,
        "write_confirmed": False,
    }
    database_url = os.getenv("DATABASE_URL")
    if any((record_run, record_quality, record_lineage)) and not database_url:
        raise RuntimeError("DATABASE_URL is required when run history, quality, or lineage recording is requested")
    if any((record_run, record_quality, record_lineage)):
        _require_recording_contract(confirm_write=confirm_write, live_check=live_check)
    if confirm_write:
        if not database_url:
            raise RuntimeError("DATABASE_URL is required when --confirm-write is used")
        if not live_check:
            raise RuntimeError("confirmed Polygon symbol-master writes require --live-check; fixture writes are disabled")
        with closing(_open_connection(database_url)) as connection:
            writer = SymbolMasterWriter(connection)
            write_result = writer.write(valid_records)
        summary["rows_written"] = write_result.written_count
        summary["rows_skipped"] = write_result.skipped_count
        summary["write_confirmed"] = write_result.succeeded
        stores = _RecordingStores()
        if record_run or record_quality or record_lineage:
            with closing(_open_connection(database_url)) as connection:
                stores = _RecordingStores(
                    run_store=IngestionRunStore(connection) if record_run else None,
                    quality_store=DataQualityResultStore(connection) if record_quality else None,
                    lineage_store=DataLineageStore(connection) if record_lineage else None,
                )
                _record_optional_evidence(
                    stores=stores,
                    run_id="manual_polygon_symbol_master",
                    valid_count=summary["rows_written"],
                    invalid_count=int(summary["invalid_count"]),
                    write_confirmed=bool(summary["write_confirmed"]),
                )
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run Polygon symbol master ingestion without writing to the database.")
    parser.add_argument("--live-check", action="store_true", help="Fetch Polygon tickers when POLYGON_API_KEY is present.")
    parser.add_argument(
        "--confirm-write",
        action="store_true",
        help="Require DATABASE_URL and write normalized rows through SymbolMasterWriter.",
    )
    parser.add_argument("--record-run", action="store_true", help="Persist run history when the approved contract is available.")
    parser.add_argument("--record-quality", action="store_true", help="Persist quality results when the approved contract is available.")
    parser.add_argument("--record-lineage", action="store_true", help="Persist lineage rows when the approved contract is available.")
    args = parser.parse_args(argv)
    if args.live_check and not os.getenv("POLYGON_API_KEY"):
        raise RuntimeError("POLYGON_API_KEY is required for --live-check")
    if args.confirm_write and not os.getenv("DATABASE_URL"):
        raise RuntimeError("DATABASE_URL is required when --confirm-write is used")
    summary = build_summary(
        live_check=args.live_check,
        confirm_write=args.confirm_write,
        record_run=args.record_run,
        record_quality=args.record_quality,
        record_lineage=args.record_lineage,
    )
    _emit(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
