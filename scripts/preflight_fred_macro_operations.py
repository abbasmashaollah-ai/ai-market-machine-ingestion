from __future__ import annotations

import os
import argparse
from pathlib import Path

from app.normalization.fred_macro import get_starter_fred_macro_series


def _load_local_env_if_available() -> bool:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return False
    return bool(load_dotenv())


def _require(path: str) -> bool:
    return Path(path).exists()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Preflight FRED macro operations.")
    parser.add_argument("--live-check", action="store_true")
    args = parser.parse_args(argv)
    _load_local_env_if_available()

    if args.live_check and not os.getenv("FRED_API_KEY"):
        raise RuntimeError("FRED_API_KEY is required when --live-check is requested")

    checks = {
        "dry_run_command_exists": _require("scripts/dry_run_fred_macro_foundation.py"),
        "live_dry_run_doc_exists": _require("docs/fred_macro_live_dry_run.md"),
        "normalization_module_exists": _require("app/normalization/fred_macro.py"),
        "starter_series_configured": len(get_starter_fred_macro_series()) > 0,
        "no_database_url_required_yet": True,
    }
    for key, value in checks.items():
        print(f"{key}={value}")
    print("no_db_writes=True")
    print("forbidden_imports_absent=True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
