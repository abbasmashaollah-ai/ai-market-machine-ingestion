from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/polygon_stock_day_agg_daily_vendor_listing_probe_operator_approval_record.md")


def test_polygon_stock_day_agg_daily_vendor_listing_probe_operator_approval_record_contains_required_scope_and_safety() -> None:
    assert DOC_PATH.exists(), "approval record must exist"
    text = DOC_PATH.read_text(encoding="utf-8")

    for phrase in [
        "This is a filled operator approval record for `target_gate: vendor_listing_probe`.",
        "APPROVE POLYGON STOCK DAY AGG DAILY VENDOR LISTING PROBE",
        "Operator name: Abbas Mashaollah",
        "Operator environment: `ai-market-machine-ingestion`",
        "Approval package commit: `02da11c`",
        "Repo hygiene evidence commit: `0623c57`",
        "Freshness gap from data repo: `staleness_days = 6`, `row count = 12235`, `quality valid`",
        "Target date: next eligible trading date after `2026-06-15`, or latest available trading date.",
        "This is the vendor listing/probe only.",
        "file availability",
        "expected object/key/path",
        "metadata if available",
        "suitability for later download approval",
        "vendor download",
        "quarantine write",
        "parse",
        "normalization",
        "handoff/intake generation",
        "DB write",
        "data repo mutation",
        "scheduler/backfill",
        "AI wiring",
        "Repo hygiene evidence doc: `docs/polygon_stock_day_agg_untracked_artifact_review_evidence.md`",
        "Daily vendor listing/probe approval package: `docs/polygon_stock_day_agg_daily_vendor_listing_probe_approval_package.md`",
        "Date checked",
        "Vendor object/key/path checked",
        "Availability result",
        "Metadata if available",
        "No download confirmation",
        "No file written confirmation",
        "No DB write confirmation",
        "No secrets printed confirmation",
        "Confirmation unrelated untracked files were not staged or modified",
        "Production staging load",
        "Canonical promotion",
        "Staging/deleting unrelated untracked files",
        "Operator approval record created",
        "Vendor listing/probe approved for future execution",
        "Vendor listing/probe not executed by this commit",
        "No download/quarantine/handoff/data repo mutation",
        "Stop immediately if credentials are missing.",
        "Stop immediately if endpoint, bucket, or prefix mismatch.",
        "Stop immediately if the listing response is empty or unexpected.",
        "Stop immediately if any secret would be printed.",
        "This approval record authorizes only the future metadata-only vendor listing/probe, not the probe execution itself.",
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
