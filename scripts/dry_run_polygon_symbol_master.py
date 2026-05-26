from __future__ import annotations

import argparse
import os
from contextlib import closing

from app.normalization.symbol_master import validate_symbol_record
from app.vendors.polygon_symbol_master import PolygonSymbolMasterAdapter, PolygonSymbolMasterSourceConfig
from app.writers.symbol_master_writer import SymbolMasterWriter


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


def build_summary(*, live_check: bool, confirm_write: bool) -> dict[str, object]:
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
    if confirm_write:
        database_url = os.getenv("DATABASE_URL")
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
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run Polygon symbol master ingestion without writing to the database.")
    parser.add_argument("--live-check", action="store_true", help="Fetch Polygon tickers when POLYGON_API_KEY is present.")
    parser.add_argument(
        "--confirm-write",
        action="store_true",
        help="Require DATABASE_URL and write normalized rows through SymbolMasterWriter.",
    )
    args = parser.parse_args(argv)
    if args.live_check and not os.getenv("POLYGON_API_KEY"):
        raise RuntimeError("POLYGON_API_KEY is required for --live-check")
    if args.confirm_write and not os.getenv("DATABASE_URL"):
        raise RuntimeError("DATABASE_URL is required when --confirm-write is used")
    summary = build_summary(live_check=args.live_check, confirm_write=args.confirm_write)
    _emit(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
