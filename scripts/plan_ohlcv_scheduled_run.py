from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
from typing import Iterable


DEFAULT_FMP_SYMBOLS = ("AAPL", "MSFT", "SPY")
DEFAULT_POLYGON_SYMBOLS = ("SPY", "QQQ", "IWM")


@dataclass(frozen=True)
class SchedulerPlan:
    vendor: str
    selected_symbols: tuple[str, ...]
    intended_command: str
    expected_preflight_command: str
    expected_evidence_verifier_command: str
    required_env_vars: tuple[str, ...]
    expected_record_flags: tuple[str, ...]
    schedule_allowed: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _format_flags(flags: Iterable[str]) -> str:
    return " ".join(flags)


def _build_fmp_plan(*, symbols: tuple[str, ...], as_of_date: date, timeframe: str, confirm_write: bool, record_run: bool, record_quality: bool, record_lineage: bool) -> SchedulerPlan:
    intended_command = (
        "python -m scripts.run_fmp_ohlcv_daily_update "
        + _format_flags(
            (
                *[f"--symbol {symbol}" for symbol in symbols],
                f"--as-of-date {as_of_date.isoformat()}",
                f"--timeframe {timeframe}",
                *(("--confirm-write",) if confirm_write else ("--dry-run",)),
                *(("--record-run",) if record_run else tuple()),
                *(("--record-quality",) if record_quality else tuple()),
                *(("--record-lineage",) if record_lineage else tuple()),
            )
        )
    )
    expected_preflight = (
        "python -m scripts.preflight_fmp_ohlcv_operations "
        + _format_flags(
            (
                *[f"--symbol {symbol}" for symbol in symbols],
                f"--as-of-date {as_of_date.isoformat()}",
                f"--timeframe {timeframe}",
            )
        )
    )
    expected_verifier = (
        "python -m scripts.verify_fmp_ohlcv_evidence_chain "
        + _format_flags(
            (
                f"--symbol {symbols[0]}",
                f"--start-date {as_of_date.isoformat()}",
                f"--end-date {as_of_date.isoformat()}",
                f"--timeframe {timeframe}",
                *(("--confirmed-write",) if confirm_write else tuple()),
                *(("--record-run",) if record_run else tuple()),
                *(("--record-quality",) if record_quality else tuple()),
                *(("--record-lineage",) if record_lineage else tuple()),
            )
        )
    )
    env_vars = ["FMP_API_KEY"]
    if confirm_write or record_run or record_quality or record_lineage:
        env_vars.append("DATABASE_URL")
    blockers: list[str] = []
    if confirm_write:
        warnings = ()
    else:
        warnings = ("schedule_plan_is_dry_run_only",)
    return SchedulerPlan(
        vendor="fmp",
        selected_symbols=symbols,
        intended_command=intended_command,
        expected_preflight_command=expected_preflight,
        expected_evidence_verifier_command=expected_verifier,
        required_env_vars=tuple(env_vars),
        expected_record_flags=tuple(
            flag
            for flag, enabled in (
                ("--confirm-write", confirm_write),
                ("--record-run", record_run),
                ("--record-quality", record_quality),
                ("--record-lineage", record_lineage),
            )
            if enabled
        ),
        schedule_allowed=False,
        blockers=tuple(blockers),
        warnings=tuple(warnings),
    )


def _build_polygon_plan(
    *,
    symbols: tuple[str, ...],
    start_date: date,
    end_date: date,
    timeframe: str,
) -> SchedulerPlan:
    intended_command = (
        "python -m scripts.run_polygon_ohlcv_chunked_backfill "
        + _format_flags(
            (
                *[f"--symbol {symbol}" for symbol in symbols],
                f"--start-date {start_date.isoformat()}",
                f"--end-date {end_date.isoformat()}",
                f"--timeframe {timeframe}",
            )
        )
    )
    expected_preflight = (
        "python -m scripts.preflight_polygon_ohlcv_operations "
        + _format_flags(
            (
                *[f"--symbol {symbol}" for symbol in symbols],
                f"--as-of-date {end_date.isoformat()}",
                f"--timeframe {timeframe}",
                "--source polygon_aggregates",
            )
        )
    )
    expected_verifier = (
        "python -m scripts.verify_polygon_ohlcv_evidence_chain "
        + _format_flags(
            (
                f"--symbol {symbols[0]}",
                f"--start-date {start_date.isoformat()}",
                f"--end-date {end_date.isoformat()}",
                f"--timeframe {timeframe}",
                "--confirmed-write",
                "--record-run",
                "--record-quality",
                "--record-lineage",
                "--resume-from-checkpoint",
            )
        )
    )
    blockers = ("polygon_backfill_remains_manual_only", "scheduler_contract_not_active_for_polygon")
    warnings = ("schedule_plan_is_manual_only",)
    return SchedulerPlan(
        vendor="polygon",
        selected_symbols=symbols,
        intended_command=intended_command,
        expected_preflight_command=expected_preflight,
        expected_evidence_verifier_command=expected_verifier,
        required_env_vars=("POLYGON_API_KEY", "DATABASE_URL"),
        expected_record_flags=("--confirmed-write", "--record-run", "--record-quality", "--record-lineage", "--resume-from-checkpoint"),
        schedule_allowed=False,
        blockers=blockers,
        warnings=warnings,
    )


def build_scheduler_plan(args: argparse.Namespace) -> SchedulerPlan:
    vendor = str(args.vendor)
    if vendor == "fmp":
        symbols = tuple(args.symbol) if args.symbol else DEFAULT_FMP_SYMBOLS
        if args.start_date or args.end_date:
            raise RuntimeError("FMP scheduled planning uses --as-of-date only")
        if not args.as_of_date:
            raise RuntimeError("FMP scheduled planning requires --as-of-date")
        return _build_fmp_plan(
            symbols=symbols,
            as_of_date=_parse_date(args.as_of_date),
            timeframe=args.timeframe,
            confirm_write=bool(args.confirm_write),
            record_run=bool(args.record_run),
            record_quality=bool(args.record_quality),
            record_lineage=bool(args.record_lineage),
        )
    if vendor == "polygon":
        symbols = tuple(args.symbol) if args.symbol else DEFAULT_POLYGON_SYMBOLS
        if not args.start_date or not args.end_date:
            raise RuntimeError("Polygon scheduled planning requires --start-date and --end-date")
        return _build_polygon_plan(
            symbols=symbols,
            start_date=_parse_date(args.start_date),
            end_date=_parse_date(args.end_date),
            timeframe=args.timeframe,
        )
    raise ValueError(f"unsupported vendor: {vendor}")


def _emit_plan(plan: SchedulerPlan) -> None:
    print(f"vendor={plan.vendor}")
    print(f"selected_symbols={plan.selected_symbols}")
    print(f"intended_command={plan.intended_command}")
    print(f"expected_preflight_command={plan.expected_preflight_command}")
    print(f"expected_evidence_verifier_command={plan.expected_evidence_verifier_command}")
    print(f"required_env_vars={plan.required_env_vars}")
    print(f"expected_record_flags={plan.expected_record_flags}")
    print(f"schedule_allowed={'true' if plan.schedule_allowed else 'false'}")
    print(f"blockers={','.join(plan.blockers) if plan.blockers else 'none'}")
    print(f"warnings={','.join(plan.warnings) if plan.warnings else 'none'}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Plan an OHLCV scheduled run without enabling a scheduler.")
    parser.add_argument("--vendor", choices=("fmp", "polygon"), default="fmp")
    parser.add_argument("--symbol", action="append", help="Ticker symbol.")
    parser.add_argument("--as-of-date", help="As-of date in YYYY-MM-DD format for FMP planning.")
    parser.add_argument("--start-date", help="Start date in YYYY-MM-DD format for Polygon planning.")
    parser.add_argument("--end-date", help="End date in YYYY-MM-DD format for Polygon planning.")
    parser.add_argument("--timeframe", default="1d")
    parser.add_argument("--confirm-write", action="store_true")
    parser.add_argument("--record-run", action="store_true")
    parser.add_argument("--record-quality", action="store_true")
    parser.add_argument("--record-lineage", action="store_true")
    args = parser.parse_args(argv)

    plan = build_scheduler_plan(args)
    _emit_plan(plan)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
