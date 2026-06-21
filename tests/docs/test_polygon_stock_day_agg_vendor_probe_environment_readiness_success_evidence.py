from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/polygon_stock_day_agg_vendor_probe_environment_readiness_success_evidence.md")


def test_polygon_stock_day_agg_vendor_probe_environment_readiness_success_evidence_contains_required_scope_and_safety() -> None:
    assert DOC_PATH.exists(), "success evidence must exist"
    text = DOC_PATH.read_text(encoding="utf-8")

    for phrase in [
        "Record that the local environment is ready for a vendor listing/probe retry.",
        "Readiness checker command: `python scripts/check_polygon_stock_day_agg_probe_environment_readiness.py`",
        "Environment setup checklist commit: `c4bdfdd`",
        "Readiness checker commit: `db50f4f`",
        "`boto3_available true`",
        "`readiness_passed true`",
        "`safe_to_retry_probe true`",
        "`required_config_keys_missing` empty",
        "`POLYGON_API_KEY`",
        "`POLYGON_FLAT_FILE_ACCESS_KEY_ID`",
        "`POLYGON_FLAT_FILE_SECRET_ACCESS_KEY`",
        "`POLYGON_FLAT_FILE_ENDPOINT`",
        "`POLYGON_FLAT_FILE_BUCKET`",
        "`POLYGON_FLAT_FILE_PREFIX`",
        "No secret values printed",
        "No DB URLs printed",
        "No credential values committed",
        "Only key names were documented",
        "`vendor_call_attempted false`",
        "`remote_listing_attempted false`",
        "`download_attempted false`",
        "`file_write_attempted false`",
        "`secrets_printed false`",
        "Vendor listing/probe may now be retried",
        "Probe must remain listing/probe-only",
        "No download",
        "No quarantine write",
        "No parse/normalization",
        "No handoff/intake package",
        "No scheduler/backfill",
        "No DB write",
        "No data repo mutation",
        "No AI wiring",
        "Separate download approval required if a new file is found",
        "Download",
        "Quarantine write",
        "Parse/normalization",
        "Handoff/intake generation",
        "DB write",
        "Data repo mutation",
        "Scheduler/backfill",
        "AI wiring",
        "Generated output commit",
        "Unrelated untracked file staging/deletion",
        "Secrets printed",
    ]:
        assert phrase in text

    lowered = text.lower()
    for forbidden in [
        "postgresql://",
        "postgresql+psycopg2://",
        "password=",
        "token=",
        "api key=",
    ]:
        assert forbidden not in lowered
