from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.preview_normalize_polygon_stock_day_agg_quarantine_file import (
    BENCHMARK_SYMBOL,
    SECTOR_SYMBOLS,
    preview_normalize_polygon_stock_day_agg_quarantine_file,
)

DEFAULT_INPUT_PATH = Path("outputs/quarantine/polygon_flat_files/polygon_stocks_day_aggs_2026-06-15.csv.gz")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview a local warehouse handoff candidate for Polygon stock day aggregates.")
    parser.add_argument("--file", default=str(DEFAULT_INPUT_PATH), help="Local gzip CSV file path.")
    parser.add_argument("--date", required=True, help="Requested date in YYYY-MM-DD format.")
    parser.add_argument("--sample-limit", type=int, default=5, help="Maximum number of candidate preview rows to include.")
    parser.add_argument("--output-file", default=None, help="Optional file path for the safe JSON output.")
    return parser


def _candidate_field_names() -> list[str]:
    return [
        "dataset",
        "source_vendor",
        "source_dataset",
        "asset_type",
        "symbol",
        "trade_date",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "transactions",
        "adjusted_status",
        "source_file_sha256",
        "source_file_size_bytes",
        "quarantine_path",
        "preview_only",
    ]


def _build_candidate_row(payload: dict[str, Any], source_path: str, *, source_sha256: str, source_size_bytes: int) -> dict[str, Any]:
    return {
        "dataset": "ohlcv_equity_daily",
        "source_vendor": "polygon_massive_flat_files",
        "source_dataset": "polygon_stocks_day_aggs",
        "asset_type": "equity_or_etf_unknown_at_ingestion",
        "symbol": payload["symbol"],
        "trade_date": payload["trade_date"],
        "open": payload["open"],
        "high": payload["high"],
        "low": payload["low"],
        "close": payload["close"],
        "volume": payload["volume"],
        "transactions": payload["transactions"],
        "adjusted_status": "unknown_or_vendor_default",
        "source_file_sha256": source_sha256,
        "source_file_size_bytes": source_size_bytes,
        "quarantine_path": source_path,
        "preview_only": True,
    }


def preview_polygon_stock_day_agg_warehouse_handoff_candidate(*, input_path: str | Path, requested_date: str, sample_limit: int = 5) -> dict[str, Any]:
    normalization = preview_normalize_polygon_stock_day_agg_quarantine_file(
        input_path=input_path,
        requested_date=requested_date,
        sample_limit=sample_limit,
    )
    source_path = str(Path(input_path))
    candidate_rows = [
        _build_candidate_row(
            row,
            source_path,
            source_sha256=str(normalization.get("local_file_sha256", "")),
            source_size_bytes=int(normalization.get("local_file_size_bytes", 0)),
        )
        for row in normalization.get("sample_normalized_rows", [])
    ]
    payload: dict[str, Any] = {
        **normalization,
        "normalization_preview_attempted": True,
        "warehouse_handoff_candidate_preview_attempted": True,
        "handoff_export_attempted": False,
        "candidate_dataset": "ohlcv_equity_daily",
        "candidate_source_vendor": "polygon_massive_flat_files",
        "candidate_source_dataset": "polygon_stocks_day_aggs",
        "handoff_candidate_count": int(normalization.get("normalized_candidate_count", 0)),
        "sample_handoff_candidate_rows": candidate_rows,
        "candidate_field_names": _candidate_field_names(),
    }
    return payload


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    payload = preview_polygon_stock_day_agg_warehouse_handoff_candidate(
        input_path=args.file,
        requested_date=args.date,
        sample_limit=args.sample_limit,
    )
    safe_json = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output_file:
        output_path = Path(args.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(safe_json + "\n", encoding="utf-8")
    sys.stdout.write(safe_json)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
