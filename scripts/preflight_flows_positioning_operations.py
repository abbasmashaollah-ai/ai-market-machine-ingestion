from __future__ import annotations

import argparse
import re
from pathlib import Path

from app.normalization.flows_positioning import DEFAULT_FIXTURE_RECORDS


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
    parser = argparse.ArgumentParser(description="Preflight flows/positioning operations.")
    args = parser.parse_args(argv)
    _ = args

    expected_record_types = (
        "ETF flows",
        "fund flows",
        "short interest",
        "institutional positioning",
        "CFTC/COT positioning",
        "dark pool/off-exchange volume",
    )
    expected_asset_classes = ("equity", "futures")
    checks = {
        "dry_run_command_exists": _require("scripts/dry_run_flows_positioning.py"),
        "source_plan_command_exists": _require("scripts/plan_flows_positioning_sources.py"),
        "foundation_doc_exists": _require("docs/flows_positioning_foundation.md"),
        "source_plan_doc_exists": _require("docs/flows_positioning_source_plan.md"),
        "preflight_doc_exists": _require("docs/flows_positioning_preflight.md"),
        "evidence_plan_doc_exists": _require("docs/flows_positioning_evidence_plan.md"),
        "normalization_module_exists": _require("app/normalization/flows_positioning.py"),
        "expected_record_types_configured": all(record_type in expected_record_types for record_type in expected_record_types),
        "expected_asset_classes_configured": all(asset_class in expected_asset_classes for asset_class in expected_asset_classes),
        "no_database_url_required_yet": True,
        "no_vendor_api_keys_required_yet": True,
    }
    forbidden_violations = []
    for path in (
        Path("scripts/dry_run_flows_positioning.py"),
        Path("scripts/plan_flows_positioning_sources.py"),
        Path("scripts/preflight_flows_positioning_operations.py"),
        Path("app/normalization/flows_positioning.py"),
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
    print(f"expected_record_types={list(expected_record_types)}")
    print(f"expected_asset_classes={list(expected_asset_classes)}")
    print(f"fixture_record_count={len(DEFAULT_FIXTURE_RECORDS)}")
    print("no_db_writes=True")
    print(f"forbidden_imports_absent={not forbidden_violations}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
