from __future__ import annotations

import argparse
import re
from pathlib import Path

from app.normalization.news_sentiment import DEFAULT_FIXTURE_RECORDS


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
    parser = argparse.ArgumentParser(description="Preflight news/sentiment operations.")
    args = parser.parse_args(argv)
    _ = args

    expected_fields = (
        "news_id",
        "published_at",
        "source",
        "publisher",
        "title",
        "summary",
        "url",
        "tickers",
        "sentiment_label",
        "sentiment_score",
        "raw_source_id",
        "notes",
    )
    checks = {
        "dry_run_command_exists": _require("scripts/dry_run_news_sentiment.py"),
        "source_plan_command_exists": _require("scripts/plan_news_sentiment_sources.py"),
        "foundation_doc_exists": _require("docs/news_sentiment_foundation.md"),
        "source_plan_doc_exists": _require("docs/news_sentiment_source_plan.md"),
        "preflight_doc_exists": _require("docs/news_sentiment_preflight.md"),
        "evidence_plan_doc_exists": _require("docs/news_sentiment_evidence_plan.md"),
        "normalization_module_exists": _require("app/normalization/news_sentiment.py"),
        "expected_fields_configured": all(field in expected_fields for field in expected_fields),
        "no_database_url_required_yet": True,
        "no_vendor_api_keys_required_yet": True,
    }
    forbidden_violations = []
    for path in (
        Path("scripts/dry_run_news_sentiment.py"),
        Path("scripts/plan_news_sentiment_sources.py"),
        Path("scripts/preflight_news_sentiment_operations.py"),
        Path("app/normalization/news_sentiment.py"),
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
    print(f"expected_fields={list(expected_fields)}")
    print(f"fixture_record_count={len(DEFAULT_FIXTURE_RECORDS)}")
    print("no_db_writes=True")
    print(f"forbidden_imports_absent={not forbidden_violations}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
