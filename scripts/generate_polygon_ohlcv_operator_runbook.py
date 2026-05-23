from __future__ import annotations

import argparse
from datetime import date

from scripts.preflight_polygon_ohlcv_operations import build_preflight_report
from scripts.verify_polygon_preflight_recommendations import _safe_reason


def _format_command(command: str | None) -> str:
    return command if command is not None else "None"


def _build_preflight_command(*, symbols: list[str], as_of_date: str, timeframe: str, max_requests: int, check_existing: bool) -> str:
    parts = ["python", "-m", "scripts.preflight_polygon_ohlcv_operations"]
    for symbol in symbols:
        parts.extend(["--symbol", symbol])
    parts.extend(["--as-of-date", as_of_date, "--timeframe", timeframe, "--max-requests", str(max_requests)])
    if check_existing:
        parts.append("--check-existing")
    return " ".join(parts)


def _build_recommendation_verifier_command(
    *, symbols: list[str], as_of_date: str, timeframe: str, max_requests: int, check_existing: bool
) -> str:
    parts = ["python", "-m", "scripts.verify_polygon_preflight_recommendations"]
    for symbol in symbols:
        parts.extend(["--symbol", symbol])
    parts.extend(["--as-of-date", as_of_date, "--timeframe", timeframe, "--max-requests", str(max_requests)])
    if check_existing:
        parts.append("--check-existing")
    return " ".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a Polygon OHLCV operator runbook safely.")
    parser.add_argument("--symbol", action="append", help="Ticker symbol. Defaults to SPY, QQQ, IWM.")
    parser.add_argument("--as-of-date", required=True, help="As-of date in YYYY-MM-DD format.")
    parser.add_argument("--timeframe", default="1d", help="Timeframe, default 1d.")
    parser.add_argument("--max-requests", type=int, default=10, help="Maximum request budget, default 10.")
    parser.add_argument("--include-evidence-flags", action="store_true", help="Include evidence flags in the runbook suggestions.")
    parser.add_argument("--check-existing", action="store_true", help="Read existing canonical coverage if DATABASE_URL is available.")
    args = parser.parse_args()

    symbols = args.symbol if args.symbol else ["SPY", "QQQ", "IWM"]
    per_symbol, summary = build_preflight_report(
        argparse.Namespace(
            symbol=symbols,
            as_of_date=args.as_of_date,
            timeframe=args.timeframe,
            source="polygon_aggregates",
            max_symbols=25,
            max_requests=args.max_requests,
            check_existing=args.check_existing,
        )
    )

    preflight_command = _build_preflight_command(
        symbols=symbols,
        as_of_date=args.as_of_date,
        timeframe=args.timeframe,
        max_requests=args.max_requests,
        check_existing=args.check_existing,
    )
    verifier_command = _build_recommendation_verifier_command(
        symbols=symbols,
        as_of_date=args.as_of_date,
        timeframe=args.timeframe,
        max_requests=args.max_requests,
        check_existing=args.check_existing,
    )

    runbook_status = "ready"
    if summary["request_budget_status"] == "exceeds_budget":
        runbook_status = "blocked"
    elif summary["preflight_status"] != "ready":
        runbook_status = "manual_review_needed"

    print(f"runbook_status={runbook_status}")
    print(f"step=1 preflight_command={preflight_command}")
    print(f"step=2 recommendation_verifier_command={verifier_command}")

    verifier_safe = True
    for item in per_symbol:
        safe, reason = _safe_reason(item["recommended_command"] if item["recommended_command"] is not None else None)
        verifier_safe = verifier_safe and safe
        recommendation_command = _format_command(item["recommended_command"] if item["recommended_command"] is not None else None)
        print(f"step=3 symbol={item['symbol']} recommended_command={recommendation_command}")
        print(
            f"symbol={item['symbol']} "
            f"recommended_action={item['recommended_action']} "
            f"recommended_command={recommendation_command} "
            f"recommendation_safe={'true' if safe else 'false'} "
            f"reason={reason}"
        )
        if args.include_evidence_flags:
            evidence_command = (
                f"python -m scripts.verify_polygon_ohlcv_evidence_chain --symbol {item['symbol']} "
                f"--start-date {args.as_of_date} --end-date {args.as_of_date} --timeframe {args.timeframe}"
            )
            print(f"step=4 evidence_command={evidence_command}")

    if not verifier_safe:
        runbook_status = "blocked"

    print(
        f"runbook_status={runbook_status} "
        f"symbols_total={summary['symbols_total']} "
        f"symbols_ready={summary['symbols_ready']} "
        f"symbols_needing_update={summary['symbols_needing_update']} "
        f"symbols_with_complete_evidence={summary['symbols_with_complete_evidence']} "
        f"estimated_total_requests={summary['estimated_total_requests']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
