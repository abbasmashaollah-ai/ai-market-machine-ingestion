from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/approvals/polygon_stock_day_agg_quarantine_download_approval_record.md")


def test_quarantine_download_approval_record_contains_required_scope_and_safety() -> None:
    assert DOC_PATH.exists()
    text = DOC_PATH.read_text(encoding="utf-8")

    for phrase in [
        "This is a filled operator approval record for `target_gate: quarantine_download`.",
        "APPROVE POLYGON STOCK DAY AGG QUARANTINE DOWNLOAD",
        "approved date: 2026-06-15",
        "approved key tail: 2026/06/2026-06-15.csv.gz",
        "approved filename: 2026-06-15.csv.gz",
        "approved expected size_bytes: 317857",
        "approved output boundary: local quarantine only",
        "approved action: single-object download into local quarantine path only",
        "any broad download",
        "any multi-day date range",
        "handoff artifact generation",
        "intake descriptor generation",
        "data repo mutation",
        "DB write",
        "scheduler activation",
        "daily incremental job",
        "limited backfill",
        "production warehouse mutation",
        "Gate 1 approval record path: `docs/approvals/polygon_stock_day_agg_vendor_listing_probe_approval_record.md`",
        "Gate 1 success evidence path: `docs/polygon_stock_day_agg_vendor_listing_probe_success_evidence.md`",
        "Gate 1 success evidence commit: `e68c04e`",
        "Remote listing readiness checker commit: `dd442df`",
        "Ingestion operator approval package commit: `556fe37`",
        "Ingestion production readiness preflight commit: `08e1913`",
        "Object presence from Gate 1: `true`",
        "Download attempted in Gate 1: `false`",
        "This approval record allows only the already listed object for `2026-06-15`.",
        "write only to the configured local quarantine path",
        "compute local file hash and size",
        "decompress or parse unless separately approved",
        "generate handoff artifacts",
        "write to the data repo",
        "write DB",
        "activate the scheduler",
        "Stop if the object key differs from Gate 1 evidence.",
        "Stop if the date differs from `2026-06-15`.",
        "Stop if the file size differs materially from the listed size without explanation.",
        "Stop if credentials or secrets would be printed.",
        "Stop if the output path escapes the local quarantine directory.",
        "Do not retry blindly.",
        "Preserve evidence without secrets.",
        "If rollback is approved, remove only the local quarantine file from this approved run.",
        "This approval record is limited to Gate 2 only.",
    ]:
        assert phrase in text

    for forbidden in ["approved broad download", "approved multi-day", "approved handoff generation", "approved intake descriptor generation", "approved data repo mutation", "approved db write", "approved scheduler activation", "approved daily incremental job", "approved limited backfill"]:
        assert forbidden not in text.lower()
