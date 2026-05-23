from __future__ import annotations

import argparse

from scripts.preflight_polygon_ohlcv_operations import build_preflight_report


ALLOWED_MODULES = {
    "scripts.run_polygon_ohlcv_daily_update",
    "scripts.run_polygon_ohlcv_chunked_backfill",
    "scripts.verify_polygon_ohlcv_evidence_chain",
    "scripts.fill_polygon_ohlcv_gaps",
}


def _extract_module(command: str | None) -> str | None:
    if not command:
        return None
    parts = command.split()
    if len(parts) < 3 or parts[0] != "python" or parts[1] != "-m":
        return None
    return parts[2]


def _safe_reason(command: str | None) -> tuple[bool, str]:
    if not command:
        return True, "none"
    if "DATABASE_URL" in command:
        return False, "contains DATABASE_URL"
    if "POLYGON_API_KEY" in command:
        return False, "contains POLYGON_API_KEY"
    if "--confirm-write" in command:
        return False, "contains --confirm-write"
    if not command.startswith("python -m scripts."):
        return False, "command does not start with python -m scripts."
    module = _extract_module(command)
    if module not in ALLOWED_MODULES:
        return False, "command target not in allowlist"
    return True, "ok"


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Polygon OHLCV preflight recommendations safely.")
    parser.add_argument("--symbol", action="append", help="Ticker symbol. Defaults to SPY, QQQ, IWM.")
    parser.add_argument("--as-of-date", required=True, help="As-of date in YYYY-MM-DD format.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    parser.add_argument("--source", default="polygon_aggregates", help="Source filter, default polygon_aggregates.")
    parser.add_argument("--max-symbols", type=int, default=25, help="Maximum symbol count, default 25.")
    parser.add_argument("--max-requests", type=int, default=10, help="Maximum request budget, default 10.")
    parser.add_argument("--check-existing", action="store_true", help="Read existing canonical coverage if DATABASE_URL is available.")
    args = parser.parse_args()

    per_symbol, summary = build_preflight_report(args)
    safe_count = 0
    unsafe_count = 0
    for item in per_symbol:
        safe, reason = _safe_reason(item["recommended_command"] if item["recommended_command"] is not None else None)
        if safe:
            safe_count += 1
        else:
            unsafe_count += 1
        print(
            f"symbol={item['symbol']} "
            f"recommended_action={item['recommended_action']} "
            f"recommendation_safe={'true' if safe else 'false'} "
            f"reason={reason}"
        )

    verification_status = "pass" if unsafe_count == 0 else "fail"
    print(
        f"recommendations_total={summary['symbols_total']} "
        f"recommendations_safe={safe_count} "
        f"recommendations_unsafe={unsafe_count} "
        f"recommendation_verification_status={verification_status}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
