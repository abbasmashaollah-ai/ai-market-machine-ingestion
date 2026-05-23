from __future__ import annotations

import argparse
import os

from scripts.persist_fred_macro import load_local_env_if_available
from scripts.run_polygon_ohlcv_scheduler_cycle import _scheduler_enabled


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the Polygon OHLCV scheduler is disabled by default.")
    parser.add_argument("--enable-scheduler-cycle", action="store_true", help="Optional explicit enable flag to inspect.")
    args = parser.parse_args()

    load_local_env_if_available()
    scheduler_enabled_env = os.getenv("ENABLE_POLYGON_OHLCV_SCHEDULER", "").lower() == "true"
    default_enabled, _ = _scheduler_enabled(argparse.Namespace(enable_scheduler_cycle=False))
    explicit_enabled, reason = _scheduler_enabled(args)
    railway_startup_safe = not scheduler_enabled_env and not args.enable_scheduler_cycle and not default_enabled

    print(f"scheduler_enabled_env={'true' if scheduler_enabled_env else 'false'}")
    print("enable_flag_required=true")
    print(f"default_status={'scheduler_disabled' if not default_enabled else 'scheduler_enabled'}")
    print(f"railway_startup_safe={'true' if railway_startup_safe else 'false'}")
    print(f"explicit_enable_status={'scheduler_disabled' if not explicit_enabled else 'scheduler_enabled'}")
    print(f"explicit_enable_reason={reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
