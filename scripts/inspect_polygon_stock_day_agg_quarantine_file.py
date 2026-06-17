from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

BENCHMARK_SYMBOL = "SPY"
SECTOR_SYMBOLS = ["XLB", "XLC", "XLE", "XLF", "XLI", "XLK", "XLP", "XLRE", "XLU", "XLV", "XLY"]
DEFAULT_INPUT_PATH = Path("outputs/quarantine/polygon_flat_files/polygon_stocks_day_aggs_2026-06-15.csv.gz")
DEFAULT_DATE = "2026-06-15"


@dataclass(frozen=True, slots=True)
class NumericSummary:
    field_name: str
    parsed_count: int
    failed_count: int


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect a local Polygon stock day aggregates quarantine file.")
    parser.add_argument("--file", default=str(DEFAULT_INPUT_PATH), help="Local gzip CSV file path.")
    parser.add_argument("--date", required=True, help="Requested date in YYYY-MM-DD format.")
    parser.add_argument("--output-file", default=None, help="Optional file path for the safe JSON output.")
    return parser


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_float(value: str) -> tuple[float | None, bool]:
    try:
        return float(value), True
    except Exception:
        return None, False


def _parse_date_value(value: str) -> str | None:
    text = str(value).strip()
    if not text:
        return None
    if len(text) >= 10 and text[4] == "-" and text[7] == "-":
        return text[:10]
    try:
        numeric = int(float(text))
    except Exception:
        return None
    if numeric > 10_000_000_000:
        numeric //= 1_000_000_000
    elif numeric > 10_000_000_000_000:
        numeric //= 1_000_000
    return datetime.fromtimestamp(numeric, tz=timezone.utc).date().isoformat()


def _read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        header = list(reader.fieldnames or [])
        rows = [dict(row) for row in reader]
    return header, rows


def _header_aliases(header_fields: list[str]) -> dict[str, str]:
    lower = {field.lower(): field for field in header_fields}
    aliases = {}
    for target in ("ticker", "symbol", "date", "window_start", "open", "high", "low", "close", "volume", "transactions"):
        if target in lower:
            aliases[target] = lower[target]
    return aliases


def inspect_polygon_stock_day_agg_quarantine_file(*, input_path: str | Path, requested_date: str) -> dict[str, Any]:
    path = Path(input_path)
    payload: dict[str, Any] = {
        "requested_date": requested_date,
        "local_file_exists": path.exists(),
        "local_file_size_bytes": path.stat().st_size if path.exists() else 0,
        "local_file_sha256": _sha256_file(path) if path.exists() else "",
        "decompression_attempted": False,
        "parse_attempted": False,
        "export_attempted": False,
        "db_write_attempted": False,
        "ingestion_attempted": False,
        "scheduler_activation_attempted": False,
        "production_mutation_attempted": False,
        "vendor_call_attempted": False,
        "download_attempted": False,
        "benchmark_symbol": BENCHMARK_SYMBOL,
        "required_sector_symbols": SECTOR_SYMBOLS,
        "blockers": [
            "inspection-only local quarantine parse is allowed",
            "no vendor calls, downloads, exports, DB writes, ingestion, scheduler activation, or production mutation are permitted",
        ],
    }
    if not path.exists():
        payload.update(
            {
                "header_fields": [],
                "header_field_count": 0,
                "row_count": 0,
                "sampled_row_count": 0,
                "symbol_count": 0,
                "benchmark_symbol_present": False,
                "required_sector_symbols_present": [],
                "required_sector_symbols_missing": SECTOR_SYMBOLS,
                "min_date_seen": None,
                "max_date_seen": None,
                "date_matches_requested_date": False,
                "numeric_field_parse_summary": [],
                "safe_sample_rows": [],
            }
        )
        return payload

    payload["decompression_attempted"] = True
    payload["parse_attempted"] = True
    header_fields, rows = _read_rows(path)
    aliases = _header_aliases(header_fields)
    symbol_field = aliases.get("ticker") or aliases.get("symbol")
    date_field = aliases.get("date") or aliases.get("window_start")
    numeric_fields = [field for field in ("open", "high", "low", "close", "volume", "transactions") if field in aliases]

    symbols = []
    parsed_dates: list[str] = []
    safe_sample_rows = []
    numeric_summaries: list[dict[str, Any]] = []
    for field in numeric_fields:
        parsed = failed = 0
        for row in rows:
            _, ok = _safe_float(str(row.get(aliases[field], "")).strip())
            if ok:
                parsed += 1
            else:
                failed += 1
        numeric_summaries.append({"field_name": field, "parsed_count": parsed, "failed_count": failed})

    for row in rows:
        if symbol_field:
            symbol = str(row.get(symbol_field, "")).strip()
            if symbol:
                symbols.append(symbol)
        if date_field:
            value = str(row.get(date_field, "")).strip()
            if value:
                parsed_date = _parse_date_value(value)
                if parsed_date:
                    parsed_dates.append(parsed_date)
        if len(safe_sample_rows) < 3:
            safe_sample_rows.append(
                {
                    "symbol": str(row.get(symbol_field, "")).strip() if symbol_field else None,
                    "date": _parse_date_value(str(row.get(date_field, "")).strip()) if date_field else None,
                }
            )

    unique_symbols = sorted(set(symbols))
    present_sector_symbols = [symbol for symbol in SECTOR_SYMBOLS if symbol in unique_symbols]
    missing_sector_symbols = [symbol for symbol in SECTOR_SYMBOLS if symbol not in unique_symbols]
    payload.update(
        {
            "header_fields": header_fields,
            "header_field_count": len(header_fields),
            "row_count": len(rows),
            "sampled_row_count": len(safe_sample_rows),
            "safe_sample_rows": safe_sample_rows,
            "symbol_count": len(unique_symbols),
            "benchmark_symbol_present": BENCHMARK_SYMBOL in unique_symbols,
            "required_sector_symbols_present": present_sector_symbols,
            "required_sector_symbols_missing": missing_sector_symbols,
            "min_date_seen": min(parsed_dates) if parsed_dates else None,
            "max_date_seen": max(parsed_dates) if parsed_dates else None,
            "date_matches_requested_date": bool(parsed_dates) and all(day == requested_date for day in parsed_dates),
            "numeric_field_parse_summary": numeric_summaries,
        }
    )
    return payload


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    payload = inspect_polygon_stock_day_agg_quarantine_file(input_path=args.file, requested_date=args.date)
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
