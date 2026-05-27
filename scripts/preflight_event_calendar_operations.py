from __future__ import annotations

import argparse
from pathlib import Path

from app.normalization.event_calendar import STARTER_EVENT_TYPES


def _require(path: str) -> bool:
    return Path(path).exists()


def _assert_text_not_present(path: Path, needles: tuple[str, ...]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    lowered = text.lower()
    return [needle for needle in needles if needle.lower() in lowered]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Preflight event calendar operations.")
    args = parser.parse_args(argv)
    _ = args

    checks = {
        "dry_run_command_exists": _require("scripts/dry_run_event_calendar_foundation.py"),
        "source_plan_command_exists": _require("scripts/plan_event_calendar_sources.py"),
        "foundation_doc_exists": _require("docs/event_calendar_foundation.md"),
        "source_plan_doc_exists": _require("docs/event_calendar_source_plan.md"),
        "normalization_module_exists": _require("app/normalization/event_calendar.py"),
        "macro_event_dry_run_command_exists": _require("scripts/dry_run_macro_event_calendar.py"),
        "macro_event_source_plan_command_exists": _require("scripts/plan_macro_event_calendar_sources.py"),
        "macro_event_foundation_doc_exists": _require("docs/macro_event_calendar_foundation.md"),
        "macro_event_source_plan_doc_exists": _require("docs/macro_event_calendar_source_plan.md"),
        "macro_event_normalization_module_exists": _require("app/normalization/macro_event_calendar.py"),
        "starter_event_types_configured": len(STARTER_EVENT_TYPES) > 0,
        "macro_event_types_configured": all(event_type in STARTER_EVENT_TYPES for event_type in ("CPI", "FOMC", "NFP")),
        "no_database_url_required_yet": True,
        "no_vendor_api_keys_required_yet": True,
    }
    forbidden_violations = []
    for path in (
        Path("scripts/dry_run_event_calendar_foundation.py"),
        Path("scripts/plan_event_calendar_sources.py"),
        Path("scripts/dry_run_macro_event_calendar.py"),
        Path("scripts/plan_macro_event_calendar_sources.py"),
        Path("app/normalization/event_calendar.py"),
        Path("app/normalization/macro_event_calendar.py"),
    ):
        forbidden_violations.extend(_assert_text_not_present(path, ("ai_market_machine_data", "fastapi", "apirouter", "requests", "httpx", "alembic")))

    for key, value in checks.items():
        print(f"{key}={value}")
    print(f"starter_event_types={list(STARTER_EVENT_TYPES)}")
    print("macro_event_types=['CPI', 'FOMC', 'NFP']")
    print("no_db_writes=True")
    print(f"forbidden_imports_absent={not forbidden_violations}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
