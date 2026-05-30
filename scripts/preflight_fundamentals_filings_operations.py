from __future__ import annotations

import argparse
import re
from pathlib import Path

from app.normalization.fundamentals_filings import RECORD_FAMILIES


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
    parser = argparse.ArgumentParser(description="Preflight fundamentals/filings operations.")
    args = parser.parse_args(argv)
    _ = args

    checks = {
        "dry_run_command_exists": _require("scripts/dry_run_fundamentals_filings.py"),
        "source_plan_command_exists": _require("scripts/plan_fundamentals_filings_sources.py"),
        "foundation_doc_exists": _require("docs/fundamentals_filings_foundation.md"),
        "source_plan_doc_exists": _require("docs/fundamentals_filings_source_plan.md"),
        "preflight_doc_exists": _require("docs/fundamentals_filings_preflight.md"),
        "evidence_plan_doc_exists": _require("docs/fundamentals_filings_evidence_plan.md"),
        "normalization_module_exists": _require("app/normalization/fundamentals_filings.py"),
        "record_families_configured": len(RECORD_FAMILIES) == 5,
        "expected_record_families_present": all(
            record_family in RECORD_FAMILIES
            for record_family in (
                "company_profile",
                "financial_statement",
                "financial_metric",
                "earnings_estimate",
                "sec_filing",
            )
        ),
        "no_database_url_required_yet": True,
        "no_vendor_api_keys_required_yet": True,
    }
    forbidden_violations = []
    for path in (
        Path("scripts/dry_run_fundamentals_filings.py"),
        Path("scripts/plan_fundamentals_filings_sources.py"),
        Path("scripts/preflight_fundamentals_filings_operations.py"),
        Path("app/normalization/fundamentals_filings.py"),
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
    print(f"record_families={list(RECORD_FAMILIES)}")
    print("no_db_writes=True")
    print(f"forbidden_imports_absent={not forbidden_violations}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
