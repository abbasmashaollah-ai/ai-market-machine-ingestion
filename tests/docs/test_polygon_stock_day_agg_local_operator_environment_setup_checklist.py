from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/polygon_stock_day_agg_local_operator_environment_setup_checklist.md")


def test_polygon_stock_day_agg_local_operator_environment_setup_checklist_contains_required_scope_and_safety() -> None:
    assert DOC_PATH.exists(), "checklist doc must exist"
    text = DOC_PATH.read_text(encoding="utf-8")

    for phrase in [
        "Operator-only checklist to prepare the local environment for a safe vendor listing/probe retry.",
        "`boto3` declared but unavailable in the active environment",
        "Required Polygon flat-file config keys missing",
        "`safe_to_retry_probe` false",
        "Activate the project virtual environment",
        "Install dependencies through the repo’s normal local install process",
        "Do not add new dependency declarations unless needed later",
        "Do not commit environment or lock changes unless intentionally reviewed",
        "`POLYGON_API_KEY`",
        "`POLYGON_FLAT_FILE_ACCESS_KEY_ID`",
        "`POLYGON_FLAT_FILE_SECRET_ACCESS_KEY`",
        "`POLYGON_FLAT_FILE_ENDPOINT`",
        "`POLYGON_FLAT_FILE_BUCKET`",
        "`POLYGON_FLAT_FILE_PREFIX`",
        "Never paste values into docs",
        "Never commit `.env` files unless explicitly designed as non-secret templates",
        "Never print values in terminal logs shared back to ChatGPT/Codex",
        "Check variable presence without printing values",
        "python scripts/check_polygon_stock_day_agg_probe_environment_readiness.py",
        "`readiness_passed true`",
        "`safe_to_retry_probe true`",
        "`vendor_call_attempted false`",
        "`remote_listing_attempted false`",
        "`download_attempted false`",
        "`file_write_attempted false`",
        "`secrets_printed false`",
        "Only retry vendor listing/probe after `readiness_passed` true and `safe_to_retry_probe` true",
        "Vendor probe retry must still be listing/probe-only",
        "No download/quarantine write/parse/normalization/handoff",
        "Separate approval required before any download",
        "Vendor call/listing/probe by this checklist",
        "Download",
        "Quarantine write",
        "Parse/normalization",
        "Handoff/intake generation",
        "Scheduler/backfill",
        "DB write",
        "Data repo mutation",
        "Production staging load",
        "Canonical promotion",
        "AI wiring",
        "Generated output commit",
        "Unrelated untracked file staging/deletion",
        "Secrets printed",
    ]:
        assert phrase in text

    assert "71ee22d" in text
    assert "db50f4f" in text

    lowered = text.lower()
    for forbidden in [
        "postgresql://",
        "postgresql+psycopg2://",
        "password=",
        "token=",
        "api key=",
    ]:
        assert forbidden not in lowered
