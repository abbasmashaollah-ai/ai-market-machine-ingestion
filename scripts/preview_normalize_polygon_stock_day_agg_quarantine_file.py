from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

BENCHMARK_SYMBOL = "SPY"
SECTOR_SYMBOLS = ["XLB", "XLC", "XLE", "XLF", "XLI", "XLK", "XLP", "XLRE", "XLU", "XLV", "XLY"]
DEFAULT_INPUT_PATH = Path("outputs/quarantine/polygon_flat_files/polygon_stocks_day_aggs_2026-06-15.csv.gz")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview-normalize a local Polygon stock day aggregates quarantine file.")
    parser.add_argument("--file", default=str(DEFAULT_INPUT_PATH), help="Local gzip CSV file path.")
    parser.add_argument("--date", required=True, help="Requested date in YYYY-MM-DD format.")
    parser.add_argument("--sample-limit", type=int, default=5, help="Maximum number of normalized preview rows to include.")
    parser.add_argument("--output-file", default=None, help="Optional file path for the safe JSON output.")
    return parser


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
    digits = len(str(abs(numeric)))
    if digits >= 19:
        numeric //= 1_000_000_000
    elif digits >= 16:
        numeric //= 1_000_000
    elif digits >= 13:
        numeric //= 1_000
    try:
        return datetime.fromtimestamp(numeric, tz=timezone.utc).date().isoformat()
    except Exception:
        return None


def _safe_float(value: Any) -> tuple[float | None, bool]:
    try:
        return float(str(value).strip()), True
    except Exception:
        return None, False


def _safe_int(value: Any) -> tuple[int | None, bool]:
    try:
        return int(float(str(value).strip())), True
    except Exception:
        return None, False


def _read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), [dict(row) for row in reader]


def _header_aliases(header_fields: list[str]) -> dict[str, str]:
    lower = {field.lower(): field for field in header_fields}
    aliases = {}
    for target in ("ticker", "symbol", "window_start", "date", "open", "high", "low", "close", "volume", "transactions"):
        if target in lower:
            aliases[target] = lower[target]
    return aliases


def _normalize_row(row: dict[str, str], aliases: dict[str, str], requested_date: str) -> tuple[dict[str, Any] | None, list[str]]:
    reasons: list[str] = []
    symbol = str(row.get(aliases.get("ticker", ""), "") or row.get(aliases.get("symbol", ""), "")).strip()
    if not symbol:
        reasons.append("missing_symbol")

    trade_date = requested_date
    if "date" in aliases:
        parsed = _parse_date_value(row.get(aliases["date"], ""))
        if parsed is None:
            reasons.append("invalid_trade_date")
        elif parsed != requested_date:
            reasons.append("trade_date_mismatch")
        else:
            trade_date = parsed
    elif "window_start" in aliases:
        parsed = _parse_date_value(row.get(aliases["window_start"], ""))
        if parsed is None:
            reasons.append("invalid_trade_date")
        elif parsed != requested_date:
            reasons.append("trade_date_mismatch")
        else:
            trade_date = parsed

    numeric_fields = {}
    for field in ("open", "high", "low", "close"):
        raw = row.get(aliases.get(field, ""), "")
        value, ok = _safe_float(raw)
        if not ok:
            reasons.append(f"invalid_{field}")
        numeric_fields[field] = value

    volume_value, volume_ok = _safe_float(row.get(aliases.get("volume", ""), ""))
    if not volume_ok:
        reasons.append("invalid_volume")

    transactions_raw = row.get(aliases.get("transactions", ""), "")
    transactions_value = None
    if str(transactions_raw).strip() != "":
        transactions_value, transactions_ok = _safe_int(transactions_raw)
        if not transactions_ok:
            reasons.append("invalid_transactions")

    if reasons:
        return None, reasons

    return (
        {
            "symbol": symbol,
            "trade_date": trade_date,
            "open": numeric_fields["open"],
            "high": numeric_fields["high"],
            "low": numeric_fields["low"],
            "close": numeric_fields["close"],
            "volume": volume_value,
            "transactions": transactions_value,
            "source_dataset": "polygon_stocks_day_aggs",
            "source_vendor": "polygon_massive_flat_files",
            "adjusted_status": "unknown_or_vendor_default",
            "preview_only": True,
        },
        [],
    )


def preview_normalize_polygon_stock_day_agg_quarantine_file(*, input_path: str | Path, requested_date: str, sample_limit: int = 5) -> dict[str, Any]:
    path = Path(input_path)
    payload: dict[str, Any] = {
        "requested_date": requested_date,
        "local_file_exists": path.exists(),
        "local_file_size_bytes": path.stat().st_size if path.exists() else 0,
        "local_file_sha256": _sha256_file(path) if path.exists() else "",
        "decompression_attempted": False,
        "parse_attempted": False,
        "normalization_preview_attempted": False,
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
            "preview-only local quarantine normalization is allowed",
            "no vendor calls, downloads, exports, DB writes, ingestion, scheduler activation, or production mutation are permitted",
        ],
    }
    if not path.exists():
        payload.update(
            {
                "raw_header_fields": [],
                "raw_row_count": 0,
                "normalized_candidate_count": 0,
                "rejected_row_count": 0,
                "rejection_reasons_summary": {},
                "benchmark_symbol_present": False,
                "required_sector_symbols_present": [],
                "required_sector_symbols_missing": SECTOR_SYMBOLS,
                "min_trade_date": None,
                "max_trade_date": None,
                "trade_date_matches_requested_date": False,
                "sample_normalized_rows": [],
                "numeric_validation_summary": {},
            }
        )
        return payload

    payload["decompression_attempted"] = True
    payload["parse_attempted"] = True
    payload["normalization_preview_attempted"] = True
    header_fields, rows = _read_rows(path)
    aliases = _header_aliases(header_fields)

    normalized_rows: list[dict[str, Any]] = []
    rejection_counter: Counter[str] = Counter()
    numeric_validation = defaultdict(lambda: {"parsed_count": 0, "failed_count": 0})
    trade_dates: list[str] = []
    symbols: list[str] = []

    for row in rows:
        normalized, reasons = _normalize_row(row, aliases, requested_date)
        if normalized is None:
            rejection_counter.update(reasons)
            continue

        normalized_rows.append(normalized)
        trade_dates.append(normalized["trade_date"])
        symbols.append(normalized["symbol"])

        for field in ("open", "high", "low", "close", "volume"):
            if normalized[field] is None:
                numeric_validation[field]["failed_count"] += 1
            else:
                numeric_validation[field]["parsed_count"] += 1
        if normalized["transactions"] is None:
            numeric_validation["transactions"]["failed_count"] += 1
        else:
            numeric_validation["transactions"]["parsed_count"] += 1

    unique_symbols = sorted(set(symbols))
    present_sector_symbols = [symbol for symbol in SECTOR_SYMBOLS if symbol in unique_symbols]
    missing_sector_symbols = [symbol for symbol in SECTOR_SYMBOLS if symbol not in unique_symbols]
    payload.update(
        {
            "raw_header_fields": header_fields,
            "raw_row_count": len(rows),
            "normalized_candidate_count": len(normalized_rows),
            "rejected_row_count": len(rows) - len(normalized_rows),
            "rejection_reasons_summary": dict(sorted(rejection_counter.items())),
            "benchmark_symbol_present": BENCHMARK_SYMBOL in unique_symbols,
            "required_sector_symbols_present": present_sector_symbols,
            "required_sector_symbols_missing": missing_sector_symbols,
            "min_trade_date": min(trade_dates) if trade_dates else None,
            "max_trade_date": max(trade_dates) if trade_dates else None,
            "trade_date_matches_requested_date": bool(trade_dates) and all(day == requested_date for day in trade_dates),
            "sample_normalized_rows": normalized_rows[: max(0, sample_limit)],
            "numeric_validation_summary": dict(sorted(numeric_validation.items())),
        }
    )
    return payload


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    payload = preview_normalize_polygon_stock_day_agg_quarantine_file(
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
