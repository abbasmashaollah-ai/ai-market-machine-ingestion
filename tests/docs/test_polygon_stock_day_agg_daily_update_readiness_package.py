from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/polygon_stock_day_agg_daily_update_readiness_package.md")


def test_polygon_stock_day_agg_daily_update_readiness_package_contains_required_language() -> None:
    assert DOC_PATH.exists(), "readiness doc must exist"
    text = DOC_PATH.read_text(encoding="utf-8")

    for phrase in [
        "Define the ingestion-side readiness requirements for daily Polygon stock day aggregate freshness remediation.",
        "Data repo detected `staleness_days = 6`",
        "Quality valid",
        "Row count `12235`",
        "Freshness/update cadence missing",
        "Vendor date availability check",
        "Explicit vendor approval gate",
        "Quarantine download path",
        "Source file hash/size capture",
        "Parse and normalize",
        "Local handoff candidate artifact",
        "Intake package artifact",
        "Evidence docs/tests",
        "No DB writes",
        "No AI/trading logic",
        "1. Inspect vendor flat-file availability for latest eligible trading date",
        "2. Require explicit operator approval before download",
        "3. Download one approved daily file to quarantine",
        "4. Compute hash and size",
        "5. Parse locally",
        "6. Normalize rows",
        "7. Validate zero/acceptable rejects",
        "8. Generate handoff candidate",
        "9. Generate intake package",
        "10. Record evidence",
        "11. Hand off to `ai-market-machine-data` for validation/staging/canonical promotion",
        "No automatic scheduler yet",
        "No backfill",
        "No multi-day bulk update until one daily cycle is proven",
        "No DB writes",
        "No production data mutation from ingestion",
        "No secrets printed",
        "No generated outputs committed",
        "No AI Machine wiring",
        "Daily vendor listing/probe approval",
        "Daily quarantine download approval",
        "Local parse/normalization approval if needed",
        "Handoff/intake package evidence",
        "Cross-repo data intake approval in `ai-market-machine-data`",
        "Quarantine file path pattern: `outputs/quarantine/polygon_flat_files/polygon_stocks_day_aggs_<YYYY-MM-DD>.csv.gz`",
        "Handoff candidate path pattern: `outputs/handoff_candidates/polygon_stock_day_aggs/polygon_stock_day_aggs_<YYYY-MM-DD>_handoff_candidate.json`",
        "Summary path pattern: `outputs/handoff_candidates/polygon_stock_day_aggs/polygon_stock_day_aggs_<YYYY-MM-DD>_summary.json`",
        "Manifest path pattern: `outputs/handoff_candidates/polygon_stock_day_aggs/polygon_stock_day_aggs_<YYYY-MM-DD>_manifest.json`",
        "Intake package path pattern: `outputs/intake_packages/polygon_stock_day_aggs/polygon_stock_day_aggs_<YYYY-MM-DD>_<YYYY-MM-DD>_intake_package.json`",
        "Docs evidence path pattern: `docs/polygon_stock_day_agg_<topic>_evidence.md`",
        "date, source vendor, source dataset, asset type, row count, rejects, source hash, source size, descriptor hash, and artifact paths",
        "Data repo owns validation and persistence after handoff",
        "Vendor call",
        "Download",
        "Scheduler",
        "Backfill",
        "DB write",
        "Data repo mutation",
        "Production staging load",
        "Canonical promotion",
        "AI Machine wiring",
        "Create a daily vendor listing/probe approval package for the next eligible Polygon stock day aggregate date, with no download until operator approval.",
        "Existing quarantine path: `outputs/quarantine/polygon_flat_files/polygon_stocks_day_aggs_2026-06-15.csv.gz`",
        "Existing source file sha256: `ac71addad2e0ba969b76763585e7e15fc74660a13c80d31869b5cbf787df3682`",
        "Existing source size: `317857`",
        "Existing rows: `12235`",
        "Existing intake package path: `outputs/intake_packages/polygon_stock_day_aggs/polygon_stock_day_aggs_2026-06-15_2026-06-15_intake_package.json`",
        "Data repo freshness design commit: `c0c270a`",
        "without executing any vendor, database, scheduler, or AI action",
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
