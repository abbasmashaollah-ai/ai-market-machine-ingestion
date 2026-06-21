from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/polygon_stock_day_agg_daily_vendor_listing_probe_approval_package.md")


def test_polygon_stock_day_agg_daily_vendor_listing_probe_approval_package_contains_required_scope_and_safety() -> None:
    assert DOC_PATH.exists(), "approval package must exist"
    text = DOC_PATH.read_text(encoding="utf-8")

    for phrase in [
        "Request approval to perform a vendor listing/probe for the next eligible Polygon stock day aggregate flat-file date.",
        "It does not approve download, quarantine write, parse, normalization, handoff generation, or any downstream repo mutation.",
        "staleness_days",
        "reached `6`",
        "Data quality remains valid",
        "Row count remains correct",
        "Fresh daily update path must be proven",
        "Listing/probe only",
        "No download",
        "No quarantine write",
        "No parse",
        "No normalization",
        "No handoff package",
        "No data repo mutation",
        "No DB write",
        "No scheduler/backfill",
        "No AI Machine wiring",
        "Next eligible trading date after `2026-06-15`, or latest available trading date",
        "file availability, expected object path/key, metadata if available, and whether the file is suitable for a future explicit download approval",
        "Date checked",
        "Vendor object/key/path checked",
        "Availability result",
        "Metadata if available, such as size or modified timestamp",
        "No download confirmation",
        "No file written confirmation",
        "No DB write confirmation",
        "No secrets printed confirmation",
        "APPROVE POLYGON STOCK DAY AGG DAILY VENDOR LISTING PROBE",
        "Approval phrase",
        "Approver",
        "Date/time",
        "Target date or latest available",
        "Scope",
        "Non-authorized actions",
        "Post-probe evidence requirement",
        "Vendor download",
        "Quarantine write",
        "Parse/normalization",
        "Handoff/intake package generation",
        "Data repo mutation",
        "DB write",
        "Production staging load",
        "Canonical promotion",
        "Scheduler/backfill",
        "AI wiring",
        "Secrets/DB URLs",
        "After operator approval, perform listing/probe only. If file exists, create a separate daily quarantine download approval package.",
        "Daily update readiness package: `docs/polygon_stock_day_agg_daily_update_readiness_package.md`",
        "Daily update readiness package commit: `954e5f9`",
        "Freshness gap from data repo:",
        "staleness_days = 6",
        "row count = 12235",
        "quality valid",
        "Previously proven file: `outputs/quarantine/polygon_flat_files/polygon_stocks_day_aggs_2026-06-15.csv.gz`",
        "Previously proven source sha256: `ac71addad2e0ba969b76763585e7e15fc74660a13c80d31869b5cbf787df3682`",
        "Previously proven source size: `317857`",
        "Previously proven rows: `12235`",
        "metadata-only vendor listing/probe and nothing beyond that scope",
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
