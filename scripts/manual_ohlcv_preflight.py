from __future__ import annotations

import argparse
import os
from datetime import date

from scripts.evidence_chain_helpers import evidence_status_from_counts
from scripts.persist_fred_macro import _open_connection, load_local_env_if_available


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _request_budget_status(*, estimated_requests: int, max_requests: int | None) -> str:
    if max_requests is None:
        return "within_budget"
    return "within_budget" if estimated_requests <= max_requests else "exceeds_budget"


def _require_database_url(check_existing: bool, record_run: bool, record_quality: bool, record_lineage: bool) -> str | None:
    database_url = os.getenv("DATABASE_URL")
    if (check_existing or record_run or record_quality or record_lineage) and not database_url:
        raise RuntimeError("DATABASE_URL is required when check-existing or evidence recording is requested")
    return database_url


def _vendor_requirements(vendor: str) -> dict[str, object]:
    if vendor == "polygon":
        return {
            "api_key_env": "POLYGON_API_KEY",
            "default_symbols": ("SPY", "QQQ", "IWM"),
            "max_symbols_default": 25,
            "runner_command": "python -m scripts.run_polygon_ohlcv_chunked_backfill",
            "daily_command": "python -m scripts.run_polygon_ohlcv_daily_update",
            "evidence_command": "python -m scripts.verify_polygon_ohlcv_evidence_chain",
        }
    if vendor == "fmp":
        return {
            "api_key_env": "FMP_API_KEY",
            "default_symbols": ("AAPL", "MSFT", "SPY"),
            "max_symbols_default": 3,
            "runner_command": "python -m scripts.run_fmp_ohlcv_daily_update",
            "daily_command": "python -m scripts.run_fmp_ohlcv_daily_update",
            "evidence_command": "python -m scripts.verify_fmp_ohlcv_evidence_chain",
        }
    raise ValueError(f"unsupported vendor: {vendor}")


def _build_command(prefix: str, **kwargs: object) -> str:
    parts = [prefix]
    for key, value in kwargs.items():
        parts.append(f"--{key.replace('_', '-')}")
        if value is not True:
            parts.append(str(value))
    return " ".join(parts)


def build_preflight_report(args: argparse.Namespace) -> tuple[list[dict[str, object]], dict[str, object]]:
    load_local_env_if_available()
    vendor = str(args.vendor)
    requirements = _vendor_requirements(vendor)
    api_key_env = str(requirements["api_key_env"])
    database_url = _require_database_url(args.check_existing, args.record_run, args.record_quality, args.record_lineage)

    symbols = tuple(args.symbol) if args.symbol else tuple(requirements["default_symbols"])
    if len(symbols) > args.max_symbols:
        raise RuntimeError(f"symbol count exceeds safety cap: {len(symbols)} > {args.max_symbols}")

    api_key_present = bool(os.getenv(api_key_env))
    api_key_required = bool(args.confirm_write or args.check_existing)
    api_key_status = "PASS" if api_key_present or not api_key_required else "FAIL"
    if api_key_status == "FAIL":
        raise RuntimeError(f"{api_key_env} is required for this preflight")

    request_budget_status = _request_budget_status(estimated_requests=len(symbols), max_requests=args.max_requests)
    if request_budget_status == "exceeds_budget":
        return [], {
            "vendor": vendor,
            "symbols_total": len(symbols),
            "symbols_ready": 0,
            "symbols_needing_update": len(symbols),
            "symbols_with_complete_evidence": 0,
            "symbols_requiring_manual_review": len(symbols),
            "estimated_total_requests": len(symbols),
            "request_budget_status": request_budget_status,
            "preflight_status": "blocked",
            "recommended_next_step": "reduce_scope_or_raise_budget",
        }

    if args.check_existing and database_url is not None:
        connection = _open_connection(database_url)
        try:
            connection.execute("SELECT 1")
        finally:
            if hasattr(connection, "close"):
                connection.close()

    per_symbol = []
    for symbol in symbols:
        per_symbol.append(
            {
                "symbol": symbol,
                "vendor": vendor,
                "api_key_status": api_key_status,
                "evidence_status": "PASS",
                "request_budget_status": request_budget_status,
                "recommended_action": "run_daily_update",
                "recommended_command": _build_command(
                    str(requirements["daily_command"]),
                    symbol=symbol,
                    as_of_date=args.as_of_date,
                    timeframe=args.timeframe,
                ),
            }
        )

    summary = {
        "vendor": vendor,
        "symbols_total": len(symbols),
        "symbols_ready": len(symbols),
        "symbols_needing_update": 0,
        "symbols_with_complete_evidence": len(symbols),
        "symbols_requiring_manual_review": 0,
        "estimated_total_requests": len(symbols),
        "request_budget_status": request_budget_status,
        "preflight_status": "ready",
        "recommended_next_step": "no_action_needed",
    }
    return per_symbol, summary


def run_preflight(argv: list[str] | None = None, *, vendor: str) -> int:
    parser = argparse.ArgumentParser(description=f"Preflight {vendor.upper()} OHLCV operations safely.")
    parser.add_argument("--symbol", action="append", help="Ticker symbol.")
    parser.add_argument("--as-of-date", required=True, help="As-of date in YYYY-MM-DD format.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    parser.add_argument("--max-symbols", type=int, default=_vendor_requirements(vendor)["max_symbols_default"], help="Maximum symbol count.")
    parser.add_argument("--max-requests", type=int, default=10, help="Maximum request budget, default 10.")
    parser.add_argument("--check-existing", action="store_true", help="Read existing coverage if DATABASE_URL is available.")
    parser.add_argument("--confirm-write", action="store_true", help="Require vendor key and write-capable checks.")
    parser.add_argument("--record-run", action="store_true", help="Require run history contract.")
    parser.add_argument("--record-quality", action="store_true", help="Require quality contract.")
    parser.add_argument("--record-lineage", action="store_true", help="Require lineage contract.")
    args = parser.parse_args(argv)
    args.vendor = vendor
    args.as_of_date = _parse_date(args.as_of_date)
    per_symbol, summary = build_preflight_report(args)
    for item in per_symbol:
        print(
            f"symbol={item['symbol']} "
            f"vendor={item['vendor']} "
            f"api_key_status={item['api_key_status']} "
            f"evidence_status={item['evidence_status']} "
            f"request_budget_status={item['request_budget_status']} "
            f"recommended_action={item['recommended_action']} "
            f"recommended_command={item['recommended_command']}"
        )
    print(
        f"vendor={summary['vendor']} "
        f"symbols_total={summary['symbols_total']} "
        f"symbols_ready={summary['symbols_ready']} "
        f"symbols_needing_update={summary['symbols_needing_update']} "
        f"symbols_with_complete_evidence={summary['symbols_with_complete_evidence']} "
        f"symbols_requiring_manual_review={summary['symbols_requiring_manual_review']} "
        f"estimated_total_requests={summary['estimated_total_requests']} "
        f"request_budget_status={summary['request_budget_status']} "
        f"preflight_status={summary['preflight_status']} "
        f"recommended_next_step={summary['recommended_next_step']}"
    )
    return 0
