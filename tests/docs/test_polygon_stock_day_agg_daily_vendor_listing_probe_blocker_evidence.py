from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/polygon_stock_day_agg_daily_vendor_listing_probe_blocker_evidence.md")


def test_polygon_stock_day_agg_daily_vendor_listing_probe_blocker_evidence_contains_required_scope_and_safety() -> None:
    assert DOC_PATH.exists(), "blocker evidence must exist"
    text = DOC_PATH.read_text(encoding="utf-8")

    for phrase in [
        "Approval package commit: `02da11c`",
        "Operator approval record commit: `0ab6b83`",
        "APPROVE POLYGON STOCK DAY AGG DAILY VENDOR LISTING PROBE",
        "Script: `scripts/preflight_polygon_flat_file_manifest.py`",
        "Command run: `python scripts/preflight_polygon_flat_file_manifest.py --enable-remote-listing --start-date 2026-06-15 --end-date 2026-06-15 --max-days 1`",
        "No verified safe probe-only utility was found that could actually perform a remote vendor listing in this environment.",
        "Polygon flat-file configuration and `boto3` were not available",
        "config_classification: missing",
        "credentials_present: false",
        "vendor_call_attempted: false",
        "remote_object_list_attempted: false",
        "download_attempted: false",
        "manifest_entries: []",
        "remote_list_expected_tail: 2026/06/2026-06-15.csv.gz",
        "remote_list_expected_filename: 2026-06-15.csv.gz",
        "No vendor call",
        "No download",
        "No file write",
        "No quarantine write",
        "No parse",
        "No normalization",
        "No handoff",
        "No DB write",
        "No data repo mutation",
        "No scheduler activation",
        "No backfill",
        "No AI wiring",
        "Implement or identify a verified probe-only utility with tests/docs before any vendor execution is attempted.",
        "app/warehouse/news_sentiment_handoff_acceptance.py",
        "tests/warehouse/test_news_sentiment_handoff_acceptance.py",
        "outputs/handoff_candidates/polygon_stock_day_aggs/*",
        "outputs/intake_packages/polygon_stock_day_aggs/*",
        "outputs/quarantine/polygon_flat_files/*",
        "No secrets or DB URLs printed",
    ]:
        assert phrase in text

    lowered = text.lower()
    for forbidden in [
        "postgresql://",
        "postgresql+psycopg2://",
        "password=",
        "token=",
        "api key",
    ]:
        assert forbidden not in lowered
