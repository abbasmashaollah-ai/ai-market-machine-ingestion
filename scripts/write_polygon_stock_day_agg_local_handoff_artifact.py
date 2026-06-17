from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.preview_normalize_polygon_stock_day_agg_quarantine_file import (
    BENCHMARK_SYMBOL,
    SECTOR_SYMBOLS,
    _header_aliases,
    _normalize_row,
    _read_rows,
    _sha256_file,
    preview_normalize_polygon_stock_day_agg_quarantine_file,
)

DEFAULT_INPUT_PATH = Path("outputs/quarantine/polygon_flat_files/polygon_stocks_day_aggs_2026-06-15.csv.gz")
ALLOWED_OUTPUT_ROOT = Path("outputs/handoff_candidates/polygon_stock_day_aggs")
APPROVAL_PHRASE = "APPROVE POLYGON STOCK DAY AGG LOCAL HANDOFF ARTIFACT WRITE"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Write a local-only Polygon stock day aggregates handoff artifact.")
    parser.add_argument("--file", default=str(DEFAULT_INPUT_PATH), help="Local gzip CSV file path.")
    parser.add_argument("--date", required=True, help="Requested date in YYYY-MM-DD format.")
    parser.add_argument("--output-dir", required=True, help="Local output directory under outputs/handoff_candidates/polygon_stock_day_aggs/.")
    parser.add_argument("--approve-local-handoff-write", action="store_true", help="Explicit approval flag required for local writes.")
    parser.add_argument("--approval-phrase", default="", help="Required approval phrase.")
    return parser


def _validate_output_dir(output_dir: Path) -> tuple[bool, str]:
    try:
        resolved = output_dir.resolve()
        allowed = ALLOWED_OUTPUT_ROOT.resolve()
        if resolved == allowed or allowed in resolved.parents:
            return True, ""
        return False, f"output_dir must be within {ALLOWED_OUTPUT_ROOT.as_posix()}"
    except Exception:
        return False, "output_dir could not be resolved safely"


def write_polygon_stock_day_agg_local_handoff_artifact(
    *,
    input_path: str | Path,
    requested_date: str,
    output_dir: str | Path,
    approve_local_handoff_write: bool,
    approval_phrase: str,
) -> dict[str, Any]:
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    candidate_paths = {
        "summary": output_dir / f"polygon_stock_day_aggs_{requested_date}_summary.json",
        "rows": output_dir / f"polygon_stock_day_aggs_{requested_date}_rows.jsonl",
    }
    payload: dict[str, Any] = {
        "requested_date": requested_date,
        "local_handoff_write_attempted": False,
        "local_handoff_write_authorized": False,
        "output_summary_path": str(candidate_paths["summary"]),
        "output_rows_path": str(candidate_paths["rows"]),
        "output_summary_exists": False,
        "output_rows_exists": False,
        "row_count_written": 0,
        "rejected_row_count": 0,
        "benchmark_symbol": BENCHMARK_SYMBOL,
        "required_sector_symbols": SECTOR_SYMBOLS,
        "blockers": [
            "local-only handoff artifact writer is allowed only after explicit approval",
            "no vendor calls, downloads, DB writes, ingestion, scheduler activation, or production mutation are permitted",
        ],
        "vendor_call_attempted": False,
        "download_attempted": False,
        "db_write_attempted": False,
        "ingestion_attempted": False,
        "scheduler_activation_attempted": False,
        "production_mutation_attempted": False,
    }

    output_ok, output_error = _validate_output_dir(output_dir)
    if not output_ok:
        payload["blockers"].append(output_error)
        return payload
    if not approve_local_handoff_write or approval_phrase != APPROVAL_PHRASE:
        payload["blockers"].append("missing or incorrect approval phrase")
        return payload

    payload["local_handoff_write_attempted"] = True
    payload["local_handoff_write_authorized"] = True
    normalization = preview_normalize_polygon_stock_day_agg_quarantine_file(
        input_path=input_path,
        requested_date=requested_date,
        sample_limit=5,
    )
    header_fields, raw_rows = _read_rows(input_path)
    aliases = _header_aliases(header_fields)
    candidate_rows: list[dict[str, Any]] = []
    rejection_counter: Counter[str] = Counter()
    for raw_row in raw_rows:
        normalized_row, reasons = _normalize_row(raw_row, aliases, requested_date)
        if normalized_row is None:
            rejection_counter.update(reasons)
            continue
        candidate_rows.append(
            {
                "dataset": "ohlcv_equity_daily",
                "source_vendor": "polygon_massive_flat_files",
                "source_dataset": "polygon_stocks_day_aggs",
                "asset_type": "equity_or_etf_unknown_at_ingestion",
                "symbol": normalized_row["symbol"],
                "trade_date": normalized_row["trade_date"],
                "open": normalized_row["open"],
                "high": normalized_row["high"],
                "low": normalized_row["low"],
                "close": normalized_row["close"],
                "volume": normalized_row["volume"],
                "transactions": normalized_row["transactions"],
                "adjusted_status": normalized_row["adjusted_status"],
                "source_file_sha256": normalization.get("local_file_sha256", ""),
                "source_file_size_bytes": normalization.get("local_file_size_bytes", 0),
                "source_quarantine_path": str(input_path),
                "preview_or_local_handoff_only": True,
            }
        )
    output_dir.mkdir(parents=True, exist_ok=True)

    rows_path = candidate_paths["rows"]
    summary_path = candidate_paths["summary"]
    with rows_path.open("w", encoding="utf-8", newline="") as handle:
        for row in candidate_rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    summary_payload = {
        "requested_date": requested_date,
        "dataset": "ohlcv_equity_daily",
        "source_vendor": "polygon_massive_flat_files",
        "source_dataset": "polygon_stocks_day_aggs",
        "source_file_sha256": normalization.get("local_file_sha256", ""),
        "source_file_size_bytes": normalization.get("local_file_size_bytes", 0),
        "source_quarantine_path": str(input_path),
        "row_count_raw": len(raw_rows),
        "row_count_written": len(candidate_rows),
        "rejected_row_count": len(raw_rows) - len(candidate_rows),
        "rejection_reasons_summary": dict(sorted(rejection_counter.items())),
        "benchmark_symbol": BENCHMARK_SYMBOL,
        "benchmark_symbol_present": normalization.get("benchmark_symbol_present", False),
        "required_sector_symbols": SECTOR_SYMBOLS,
        "required_sector_symbols_present": normalization.get("required_sector_symbols_present", []),
        "required_sector_symbols_missing": normalization.get("required_sector_symbols_missing", SECTOR_SYMBOLS),
        "output_rows_path": str(rows_path),
        "output_summary_path": str(summary_path),
        "preview_or_local_handoff_only": True,
        "production_approved": False,
        "db_write_attempted": False,
        "vendor_call_attempted": False,
        "download_attempted": False,
        "ingestion_attempted": False,
        "scheduler_activation_attempted": False,
        "production_mutation_attempted": False,
    }
    summary_path.write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    payload.update(
        {
            "output_summary_exists": summary_path.exists(),
            "output_rows_exists": rows_path.exists(),
            "row_count_written": len(candidate_rows),
            "rejected_row_count": len(raw_rows) - len(candidate_rows),
            "candidate_dataset": "ohlcv_equity_daily",
            "candidate_source_vendor": "polygon_massive_flat_files",
            "candidate_source_dataset": "polygon_stocks_day_aggs",
            "benchmark_symbol_present": normalization.get("benchmark_symbol_present", False),
            "required_sector_symbols_present": normalization.get("required_sector_symbols_present", []),
            "required_sector_symbols_missing": normalization.get("required_sector_symbols_missing", SECTOR_SYMBOLS),
            "sample_output_rows": candidate_rows[:5],
        }
    )
    return payload


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    payload = write_polygon_stock_day_agg_local_handoff_artifact(
        input_path=args.file,
        requested_date=args.date,
        output_dir=args.output_dir,
        approve_local_handoff_write=args.approve_local_handoff_write,
        approval_phrase=args.approval_phrase,
    )
    safe_json = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    sys.stdout.write(safe_json)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
