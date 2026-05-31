from __future__ import annotations

import argparse
import re
from pathlib import Path

from app.normalization.breadth_participation import DEFAULT_FIXTURE_RECORDS


def _require(path: str) -> bool:
    return Path(path).exists()


def _assert_text_not_present(path: Path, needles: tuple[str, ...]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    lowered = text.lower()
    violations: list[str] = []
    for needle in needles:
        if re.search(needle, lowered, flags=re.MULTILINE):
            violations.append(needle)
    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Preflight breadth/participation operations.")
    args = parser.parse_args(argv)
    _ = args

    expected_metric_types = (
        "advance_decline_count",
        "new_highs_new_lows",
        "percent_above_moving_average",
        "up_down_volume",
        "sector_participation",
        "index_universe_breadth",
    )
    expected_universes = ("US equities", "S&P 500", "S&P 500 sectors", "Russell 3000")
    checks = {
        "dry_run_command_exists": _require("scripts/dry_run_breadth_participation.py"),
        "source_plan_command_exists": _require("scripts/plan_breadth_participation_sources.py"),
        "foundation_doc_exists": _require("docs/breadth_participation_foundation.md"),
        "source_plan_doc_exists": _require("docs/breadth_participation_source_plan.md"),
        "preflight_doc_exists": _require("docs/breadth_participation_preflight.md"),
        "evidence_plan_doc_exists": _require("docs/breadth_participation_evidence_plan.md"),
        "normalization_module_exists": _require("app/normalization/breadth_participation.py"),
        "expected_metric_types_configured": all(metric_type in expected_metric_types for metric_type in expected_metric_types),
        "expected_universes_configured": all(universe in expected_universes for universe in expected_universes),
        "no_database_url_required_yet": True,
        "no_vendor_api_keys_required_yet": True,
    }
    forbidden_violations = []
    for path in (
        Path("scripts/dry_run_breadth_participation.py"),
        Path("scripts/plan_breadth_participation_sources.py"),
        Path("scripts/preflight_breadth_participation_operations.py"),
        Path("app/normalization/breadth_participation.py"),
    ):
        forbidden_violations.extend(
            _assert_text_not_present(
                path,
                (
                    r"^\s*import\s+fastapi\b",
                    r"^\s*from\s+fastapi\b",
                    r"^\s*import\s+apirouter\b",
                    r"^\s*from\s+fastapi\s+import\s+apirouter\b",
                    r"^\s*import\s+requests\b",
                    r"^\s*from\s+requests\b",
                    r"^\s*import\s+httpx\b",
                    r"^\s*from\s+httpx\b",
                    r"^\s*import\s+alembic\b",
                    r"^\s*from\s+alembic\b",
                ),
            )
        )

    for key, value in checks.items():
        print(f"{key}={value}")
    print(f"expected_metric_types={list(expected_metric_types)}")
    print(f"expected_universes={list(expected_universes)}")
    print(f"fixture_record_count={len(DEFAULT_FIXTURE_RECORDS)}")
    print("no_db_writes=True")
    print(f"forbidden_imports_absent={not forbidden_violations}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
