from __future__ import annotations

import argparse
from contextlib import closing
import os

from scripts.evidence_chain_helpers import status_from_requirement
from scripts.persist_fred_macro import _open_connection, load_local_env_if_available
from app.state.data_lineage_store import DataLineageStore
from app.state.data_quality_result_store import DataQualityResultStore
from app.state.ingestion_run_store import IngestionRunStore
from app.state.runs import IngestionRun, RunStatus
from app.quality.validators import ValidationResult, ValidationSeverity, ValidationStatus


def _fetch_all(connection: object, sql: str, params: tuple[object, ...] = ()) -> list[dict[str, object]]:
    cursor = None
    try:
        if hasattr(connection, "cursor") and not hasattr(connection, "execute"):
            cursor = connection.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
        else:
            result = connection.execute(sql, params)  # type: ignore[call-arg]
            rows = result.fetchall() if hasattr(result, "fetchall") else []
        if not rows:
            return []
        first = rows[0]
        if isinstance(first, dict):
            return [row for row in rows if isinstance(row, dict)]
        columns = [desc[0] for desc in getattr(cursor, "description", [])] if cursor is not None else []
        return [dict(zip(columns, row)) for row in rows]
    finally:
        if cursor is not None and hasattr(cursor, "close"):
            cursor.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify the symbol master evidence chain safely.")
    parser.add_argument("--symbol", help="Optional canonical symbol to check.")
    parser.add_argument("--record-run", action="store_true", help="Persist run history when the approved contract is available.")
    parser.add_argument("--record-quality", action="store_true", help="Persist quality results when the approved contract is available.")
    parser.add_argument("--record-lineage", action="store_true", help="Persist lineage rows when the approved contract is available.")
    args = parser.parse_args(argv)

    load_local_env_if_available()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    connection = _open_connection(database_url)
    try:
        counts = _fetch_all(
            connection,
            """
            SELECT
                COUNT(*) AS row_count,
                COUNT(*) FILTER (WHERE active IS TRUE) AS active_count,
                COUNT(*) FILTER (WHERE active IS FALSE) AS inactive_count
            FROM public.symbol_master
            """.strip(),
        )
        count_row = counts[0] if counts else {"row_count": 0, "active_count": 0, "inactive_count": 0}
        row_count = int(count_row.get("row_count") or 0)
        active_count = int(count_row.get("active_count") or 0)
        inactive_count = int(count_row.get("inactive_count") or 0)
        symbol_found = None
        symbol_status = "PASS"
        if args.symbol:
            rows = _fetch_all(
                connection,
                """
                SELECT symbol, vendor, vendor_symbol, active, exchange, asset_type, name, currency
                FROM public.symbol_master
                WHERE symbol = %s
                LIMIT 1
                """.strip(),
                (args.symbol,),
            )
            symbol_found = bool(rows)
            symbol_status = status_from_requirement(required=True, present=symbol_found)
        evidence_status = "WARN" if row_count == 0 else "PASS"
        if args.symbol and not symbol_found:
            evidence_status = "FAIL"
        run_status = "WARN" if row_count == 0 else "PASS"
        quality_status = "WARN" if row_count == 0 else "PASS"
        lineage_status = "WARN" if row_count == 0 else "PASS"
        if args.record_run or args.record_quality or args.record_lineage:
            run_store = IngestionRunStore(connection) if args.record_run else None
            quality_store = DataQualityResultStore(connection) if args.record_quality else None
            lineage_store = DataLineageStore(connection) if args.record_lineage else None
            if run_store is not None:
                run_store.save_run(
                    IngestionRun(
                        run_id="manual_symbol_master_evidence",
                        job_id="manual_symbol_master_evidence",
                        status=RunStatus.SUCCESS if evidence_status == "PASS" else RunStatus.PARTIAL if evidence_status == "WARN" else RunStatus.FAILED,
                        rows_fetched=row_count,
                        rows_written=row_count,
                        rows_rejected=0,
                        error_count=0 if evidence_status != "FAIL" else 1,
                        metadata={"vendor": "polygon", "dataset": "symbol_master"},
                    )
                )
            if quality_store is not None:
                quality_store.save_validation_results(
                    vendor="polygon",
                    dataset="symbol_master",
                    symbol=args.symbol,
                    timeframe=None,
                    results=[
                        ValidationResult(
                            check_name="symbol_master_evidence_summary",
                            status=ValidationStatus.PASS if evidence_status == "PASS" else ValidationStatus.WARN if evidence_status == "WARN" else ValidationStatus.FAIL,
                            severity=ValidationSeverity.INFO if evidence_status == "PASS" else ValidationSeverity.WARN if evidence_status == "WARN" else ValidationSeverity.ERROR,
                            message="symbol master evidence summary",
                        )
                    ],
                    run_id="manual_symbol_master_evidence",
                    job_id=None,
                )
            if lineage_store is not None:
                lineage_store.save_chunk_lineage(
                    vendor="polygon",
                    dataset="symbol_master",
                    symbol=args.symbol,
                    timeframe=None,
                    source_endpoint=None,
                    request_params=None,
                    response_status=200 if evidence_status == "PASS" else 204 if evidence_status == "WARN" else 500,
                    row_count=row_count,
                    normalization_version="polygon.symbol_master.v1",
                    quality_status="pass" if evidence_status == "PASS" else "warn" if evidence_status == "WARN" else "fail",
                    run_id="manual_symbol_master_evidence",
                    job_id="manual_symbol_master_evidence",
                )
        print(
            f"row_count={row_count} "
            f"active_count={active_count} "
            f"inactive_count={inactive_count} "
            f"symbol={args.symbol if args.symbol else None} "
            f"symbol_found={symbol_found} "
            f"symbol_status={symbol_status} "
            f"evidence_status={evidence_status} "
            f"run_status={run_status} "
            f"quality_status={quality_status} "
            f"lineage_status={lineage_status}"
        )
    finally:
        if hasattr(connection, "close"):
            connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
