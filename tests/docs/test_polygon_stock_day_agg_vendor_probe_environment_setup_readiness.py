from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/polygon_stock_day_agg_vendor_probe_environment_setup_readiness.md")


def test_polygon_stock_day_agg_vendor_probe_environment_setup_readiness_contains_required_scope_and_safety() -> None:
    assert DOC_PATH.exists(), "setup readiness doc must exist"
    text = DOC_PATH.read_text(encoding="utf-8")

    required_phrases = [
        "Prepare the environment for a safe Polygon stock day aggregate vendor listing/probe retry.",
        "`boto3` unavailable",
        "Required Polygon flat-file config keys missing",
        "`readiness_passed` false",
        "`safe_to_retry_probe` false",
        "Dependency declaration status: already present in `pyproject.toml`",
        "`POLYGON_API_KEY`",
        "`POLYGON_FLAT_FILE_ACCESS_KEY_ID`",
        "`POLYGON_FLAT_FILE_SECRET_ACCESS_KEY`",
        "`POLYGON_FLAT_FILE_ENDPOINT`",
        "`POLYGON_FLAT_FILE_BUCKET`",
        "`POLYGON_FLAT_FILE_PREFIX`",
        "No secrets in docs",
        "No secrets in git",
        "No DB URLs",
        "No token values",
        "No command output containing secret values",
        "Install dependencies through the project’s normal local process",
        "Set required environment variables securely outside git",
        "Rerun `python scripts/check_polygon_stock_day_agg_probe_environment_readiness.py`",
        "Only retry vendor listing/probe if `readiness_passed` is true and `safe_to_retry_probe` is true",
        "Still no download",
        "Still no quarantine write",
        "Still no parse/normalization/handoff",
        "Still no DB/data repo/scheduler/backfill/AI",
        "Package installation by Codex",
        "Vendor call/listing/probe",
        "Download",
        "File write to `outputs/quarantine`",
        "Parse/normalization",
        "Handoff/intake generation",
        "DB write",
        "Data repo mutation",
        "Scheduler/backfill",
        "AI wiring",
        "Generated output commit",
        "Unrelated untracked file staging/deletion",
        "Secrets printed",
    ]
    for phrase in required_phrases:
        assert phrase in text

    assert "e16402c" in text

    lowered = text.lower()
    for forbidden in [
        "postgresql://",
        "postgresql+psycopg2://",
        "password=",
        "token=",
        "api key=",
    ]:
        assert forbidden not in lowered
