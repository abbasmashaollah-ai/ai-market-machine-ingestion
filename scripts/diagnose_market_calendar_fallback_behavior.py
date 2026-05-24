from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose market calendar fallback behavior without external calls.")
    parser.add_argument("--exchange", default="XNYS", help="Exchange code, default XNYS.")
    args = parser.parse_args()

    print(f"exchange={args.exchange}")
    print("production_calendar_available=false")
    print("current_fallback=minimal_static_helper")
    print("fallback_allowed_for=manual_tests,planning_diagnostics")
    print("fallback_forbidden_for=production_scheduler,large_backfills,flatfile_persistence,official_gap_fill")
    print("fallback_status=manual_only")
    print("required_before_production=data_calendar_schema,verified_calendar_loaded,deterministic_tests,consumer_integration")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
