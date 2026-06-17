from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/approvals/polygon_stock_day_agg_vendor_listing_probe_approval_record.md")


def test_vendor_listing_probe_approval_record_contains_required_scope_and_safety() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    for phrase in [
        "This is a filled operator approval record for `target_gate: vendor_listing_probe`.",
        "APPROVE POLYGON STOCK DAY AGG VENDOR LISTING PROBE",
        "tiny vendor listing probe only",
        "It does not approve:",
        "vendor file download",
        "quarantine download",
        "local handoff generation",
        "data repo mutation",
        "DB write",
        "scheduler activation",
        "backfill",
        "production warehouse mutation",
        "Ingestion production readiness preflight status: `READY_FOR_OPERATOR_REVIEW`",
        "Ingestion operator approval package path: `docs/polygon_stock_day_agg_ingestion_operator_approval_package.md`",
        "Cross-repo evidence bundle exists in data repo: `docs/polygon_stock_day_agg_cross_repo_ohlcv_domain_evidence_bundle.md`",
        "Ingestion operator approval package commit: `556fe37`",
        "Ingestion blocker scan fix commit: `02454e5`",
        "Ingestion `.gitkeep` placeholder fix commit: `aaaabb8`",
        "Ingestion production readiness preflight commit: `08e1913`",
        "Operator name: Abbas Mashaollah",
        "Operator role: Owner / Operator",
        "Approval record ID: `polygon-stock-day-agg-vendor-listing-probe-001`",
        "Repo: `ai-market-machine-ingestion`",
        "Approval created at UTC: `TO_BE_FILLED`",
        "Final operator signature: Abbas Mashaollah",
        "The tiny vendor listing probe may list metadata only.",
        "The tiny vendor listing probe may not:",
        "download object bytes",
        "create local output artifacts except a later approved evidence or report if separately requested",
        "mutate the data repo",
        "write DB",
        "activate the scheduler",
        "Stop immediately if credentials are missing.",
        "Stop immediately if endpoint, bucket, or prefix mismatch.",
        "Stop immediately if the listing response is empty or unexpected.",
        "Stop immediately if any secret would be printed.",
        "Do not retry blindly.",
        "Preserve command output without secrets.",
        "This approval record is limited to Gate 1 only.",
        "It does not approve quarantine download.",
        "It does not approve local handoff generation.",
        "It does not approve data-repo intake descriptor generation.",
        "It does not approve the daily incremental job.",
        "It does not approve limited backfill.",
        "It does not approve scheduler activation.",
        "no unapproved scope creep",
    ]:
        assert phrase in text

