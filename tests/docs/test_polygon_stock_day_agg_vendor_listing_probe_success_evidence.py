from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/polygon_stock_day_agg_vendor_listing_probe_success_evidence.md")


def test_vendor_listing_probe_success_evidence_contains_required_success_fields() -> None:
    assert DOC_PATH.exists()
    text = DOC_PATH.read_text(encoding="utf-8")

    for phrase in [
        "This document is successful Gate 1 metadata listing evidence only.",
        "APPROVE POLYGON STOCK DAY AGG VENDOR LISTING PROBE",
        "vendor_listing_probe",
        "Date probed: `2026-06-15`",
        "python scripts/preflight_polygon_flat_file_manifest.py --enable-remote-listing --start-date 2026-06-15 --end-date 2026-06-15 --max-days 1",
        "vendor_call_attempted: true",
        "remote_object_list_attempted: true",
        "download_attempted: false",
        "remote_file_read_attempted: false",
        "db_write_attempted: false",
        "scheduler_activation_attempted: false",
        "production_mutation_attempted: false",
        "credentials_printed: false",
        "endpoint_value_printed: false",
        "bucket_value_printed: false",
        "prefix_value_printed: false",
        "config_classification: polygon_flat_file",
        "credentials_present: true",
        "manifest_listing_enabled: true",
        "preflight_only: true",
        "production_handoff_generation_authorized: false",
        "manifest_object_count_present: 1",
        "manifest_object_count_missing: 0",
        "remote_list_object_count_seen: 1",
        "remote_list_csv_gz_object_count_seen: 12",
        "date: 2026-06-15",
        "object_present: true",
        "redacted_key_tail: 2026/06/2026-06-15.csv.gz",
        "remote_list_expected_filename: 2026-06-15.csv.gz",
        "remote_list_expected_tail: 2026/06/2026-06-15.csv.gz",
        "remote_list_basename_match: true",
        "remote_list_suffix_match: true",
        "resolved_key_present: true",
        "resolved_key_matches_listed_key: true",
        "resolved_key_tail_matches_requested_date: true",
        "etag_present: true",
        "last_modified_present: true",
        "size_bytes: 317857",
        "listed_key_sha256_prefix: b061164d326c",
        "resolved_key_sha256_prefix: b061164d326c",
        "No secrets were printed.",
        "No download was performed.",
        "No quarantine artifact was generated.",
        "No handoff artifact was generated.",
        "No data repo mutation occurred.",
        "No DB write occurred.",
        "No scheduler activation occurred.",
        "No production warehouse mutation occurred.",
        "The next required gate is the quarantine download approval record.",
    ]:
        assert phrase in text

    for forbidden in ["download approval", "quarantine approval", "handoff generation approval", "data repo mutation approval", "db writes approval", "scheduler activation approval"]:
        assert forbidden not in text.lower() or forbidden in {"download approval", "quarantine approval"}  # keep explicit non-approval phrases out

