from __future__ import annotations

import argparse
import os
from contextlib import closing
from datetime import datetime, timezone
from urllib.parse import urlparse

from app.normalization.symbol_master import (
    SymbolMasterSourceRecord,
    normalize_symbol_record,
    validate_source_record,
    validate_symbol_record,
)
from app.writers.symbol_master_writer import SymbolMasterWriter


DEFAULT_SAMPLE_SOURCE = (
    SymbolMasterSourceRecord(
        symbol="AAPL",
        active=True,
        vendor="fmp",
        source_vendor="fmp",
        source_dataset="symbol_master",
        source_sha256="fixture-source-sha256-aapl",
        source_file_name="symbol_master_fixture_aapl.json",
        source_file_path="fixtures/symbol_master/symbol_master_fixture_aapl.json",
        producer_run_id="symbol-master-fixture-run-001",
        vendor_symbol="AAPL",
        asset_type="equity",
        exchange="NASDAQ",
        name="Apple Inc.",
        currency="USD",
        first_seen_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        last_seen_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
    ),
    SymbolMasterSourceRecord(
        symbol="SPY",
        active=True,
        vendor="polygon",
        source_vendor="polygon",
        source_dataset="symbol_master",
        source_sha256="fixture-source-sha256-spy",
        source_file_name="symbol_master_fixture_spy.json",
        source_file_path="fixtures/symbol_master/symbol_master_fixture_spy.json",
        producer_run_id="symbol-master-fixture-run-001",
        vendor_symbol="SPY",
        asset_type="etf",
        exchange="NYSEARCA",
        name="SPDR S&P 500 ETF Trust",
        currency="USD",
        first_seen_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        last_seen_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
    ),
    SymbolMasterSourceRecord(
        symbol="VIX",
        active=False,
        vendor="polygon",
        source_vendor="polygon",
        source_dataset="symbol_master",
        source_sha256="fixture-source-sha256-vix",
        source_file_name="symbol_master_fixture_vix.json",
        source_file_path="fixtures/symbol_master/symbol_master_fixture_vix.json",
        producer_run_id="symbol-master-fixture-run-001",
        vendor_symbol="I:VIX",
        asset_type="index",
        exchange="CBOE",
        name="CBOE Volatility Index",
        currency="USD",
        first_seen_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        last_seen_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
    ),
)


def _is_postgres_url(database_url: str) -> bool:
    scheme = urlparse(database_url).scheme.lower()
    return scheme in {"postgresql", "postgres"}


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
    if not _is_postgres_url(database_url):
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
        "dry_run",
        "vendor_source",
    ):
        print(f"{key}={summary.get(key)}")


def build_dry_run_summary(source_records: tuple[SymbolMasterSourceRecord, ...]) -> dict[str, object]:
    normalized_records = [normalize_symbol_record(record) for record in source_records]
    source_errors = [validate_source_record(record) for record in source_records]
    valid_records = [record for record, errors in zip(normalized_records, source_errors) if not errors and not validate_symbol_record(record)]
    invalid_records = [record for record, errors in zip(normalized_records, source_errors) if errors or validate_symbol_record(record)]
    return {
        "input_count": len(source_records),
        "normalized_count": len(normalized_records),
        "valid_count": len(valid_records),
        "invalid_count": len(invalid_records),
        "dry_run": True,
        "vendor_source": "sample_fixture",
        "normalized_records": tuple(normalized_records),
        "source_errors": tuple(tuple(errors) for errors in source_errors),
        "rows_written": 0,
        "rows_skipped": 0,
        "write_confirmed": False,
    }


def build_confirmed_write_summary(source_records: tuple[SymbolMasterSourceRecord, ...], *, writer: SymbolMasterWriter) -> dict[str, object]:
    normalized_records = [normalize_symbol_record(record) for record in source_records]
    source_errors = [validate_source_record(record) for record in source_records]
    valid_records = [record for record, errors in zip(normalized_records, source_errors) if not errors and not validate_symbol_record(record)]
    invalid_records = [record for record, errors in zip(normalized_records, source_errors) if errors or validate_symbol_record(record)]
    write_result = writer.write(valid_records)
    return {
        "input_count": len(source_records),
        "normalized_count": len(normalized_records),
        "valid_count": len(valid_records),
        "invalid_count": len(invalid_records),
        "dry_run": False,
        "vendor_source": "sample_fixture",
        "normalized_records": tuple(normalized_records),
        "source_errors": tuple(tuple(errors) for errors in source_errors),
        "idempotency_keys": tuple(
            key
            for key in (
                writer._idempotency_key(record)  # noqa: SLF001 - local dry-run alignment helper
                for record in valid_records
            )
            if key
        ),
        "rows_written": write_result.written_count,
        "rows_skipped": write_result.skipped_count,
        "write_confirmed": write_result.succeeded,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Dry-run symbol master ingestion by default; use --confirm-write to persist valid rows."
    )
    parser.add_argument("--fixture", default="default", help="Use the built-in deterministic sample fixture.")
    parser.add_argument("--confirm-write", action="store_true", help="Write valid rows through SymbolMasterWriter.")
    parser.add_argument("--dry-run", action="store_true", help="Keep writer execution disabled.")
    args = parser.parse_args(argv)
    if args.fixture != "default":
        raise RuntimeError("only the default deterministic fixture is supported")
    if args.confirm_write and args.dry_run:
        raise RuntimeError("use either --confirm-write or --dry-run, not both")
    if args.confirm_write:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL is required when --confirm-write is used")
        with closing(_open_connection(database_url)) as connection:
            writer = SymbolMasterWriter(connection)
            summary = build_confirmed_write_summary(DEFAULT_SAMPLE_SOURCE, writer=writer)
    else:
        summary = build_dry_run_summary(DEFAULT_SAMPLE_SOURCE)
    _emit(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
