from __future__ import annotations

import argparse
from datetime import date


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose market calendar production upgrade readiness without external calls.")
    parser.add_argument("--exchange", default="XNYS", help="Exchange code, default XNYS.")
    parser.add_argument("--start-date", required=True, help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", required=True, help="End date in YYYY-MM-DD format.")
    args = parser.parse_args()

    start_date = _parse_date(args.start_date)
    end_date = _parse_date(args.end_date)

    print(f"exchange={args.exchange}")
    print(f"start_date={start_date.isoformat()}")
    print(f"end_date={end_date.isoformat()}")
    print("current_calendar_mode=minimal_explicit_closures")
    print("production_calendar_required=true")
    print("holiday_calendar_required=true")
    print("special_closures_required=true")
    print("early_closes_required=true")
    print("timezone_required=America/New_York")
    print("deterministic_tests_required=true")
    print("flatfile_alignment_required=true")
    print("scheduler_alignment_required=true")
    print("calendar_upgrade_status=planning_only_not_enabled")
    print("required_before_production_scheduler=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
