from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/polygon_stock_day_agg_vendor_listing_probe_evidence.md")


def test_vendor_listing_probe_evidence_includes_required_language() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    for phrase in [
        "Approval record path: `docs/approvals/polygon_stock_day_agg_vendor_listing_probe_approval_record.md`",
        "APPROVE POLYGON STOCK DAY AGG VENDOR LISTING PROBE",
        "Target gate: `vendor_listing_probe`",
        "Date probed: `2026-06-15`",
        "python scripts/preflight_polygon_flat_file_manifest.py --enable-remote-listing --start-date 2026-06-15 --end-date 2026-06-15 --max-days 1",
        "The probe remained metadata-only and did not download object bytes.",
        "config_classification: missing",
        "credentials_present: false",
        "vendor_call_attempted: false",
        "remote_object_list_attempted: false",
        "download_attempted: false",
        "remote_list_object_count_seen: 0",
        "remote_list_csv_gz_object_count_seen: 0",
        "manifest_entries: []",
        "No secrets were printed.",
        "No endpoint, bucket, or prefix secret values were printed.",
        "No object presence result was returned because the remote listing did not run in this environment.",
        "2026/06/2026-06-15.csv.gz",
        "2026-06-15.csv.gz",
        "No download",
        "No quarantine artifact generated",
        "No handoff artifact generated",
        "No data repo mutation",
        "No DB write",
        "No scheduler activation",
        "The next gate required is quarantine download approval.",
    ]:
        assert phrase in text

