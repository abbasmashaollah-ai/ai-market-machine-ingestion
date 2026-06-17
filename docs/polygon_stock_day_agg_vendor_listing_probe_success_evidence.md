# Polygon Stock Day Agg Vendor Listing Probe Success Evidence

This document is successful Gate 1 metadata listing evidence only.

It does not grant download approval.
It does not grant quarantine approval.
It does not grant handoff generation.
It does not grant data repo mutation.
It does not grant DB writes.
It does not grant scheduler activation.
It does not grant backfill.

## Approval Reference

- Approval record path: `docs/approvals/polygon_stock_day_agg_vendor_listing_probe_approval_record.md`
- Approval phrase used: `APPROVE POLYGON STOCK DAY AGG VENDOR LISTING PROBE`
- Target gate: `vendor_listing_probe`
- Date probed: `2026-06-15`

## Successful Command Used

`python scripts/preflight_polygon_flat_file_manifest.py --enable-remote-listing --start-date 2026-06-15 --end-date 2026-06-15 --max-days 1`

## Successful Output Summary

- `vendor_call_attempted: true`
- `remote_object_list_attempted: true`
- `download_attempted: false`
- `remote_file_read_attempted: false`
- `db_write_attempted: false`
- `scheduler_activation_attempted: false`
- `production_mutation_attempted: false`
- `credentials_printed: false`
- `endpoint_value_printed: false`
- `bucket_value_printed: false`
- `prefix_value_printed: false`
- `config_classification: polygon_flat_file`
- `credentials_present: true`
- `manifest_listing_enabled: true`
- `preflight_only: true`
- `production_handoff_generation_authorized: false`
- `manifest_object_count_present: 1`
- `manifest_object_count_missing: 0`
- `remote_list_object_count_seen: 1`
- `remote_list_csv_gz_object_count_seen: 12`

## Manifest Entry

- `date: 2026-06-15`
- `object_present: true`
- `redacted_key_tail: 2026/06/2026-06-15.csv.gz`
- `remote_list_expected_filename: 2026-06-15.csv.gz`
- `remote_list_expected_tail: 2026/06/2026-06-15.csv.gz`
- `remote_list_basename_match: true`
- `remote_list_suffix_match: true`
- `resolved_key_present: true`
- `resolved_key_matches_listed_key: true`
- `resolved_key_tail_matches_requested_date: true`
- `etag_present: true`
- `last_modified_present: true`
- `size_bytes: 317857`
- `listed_key_sha256_prefix: b061164d326c`
- `resolved_key_sha256_prefix: b061164d326c`

## No Secret Printing

- No secrets were printed.
- No endpoint value was printed.
- No bucket value was printed.
- No prefix value was printed.

## No Side Effects

- No download was performed.
- No quarantine artifact was generated.
- No handoff artifact was generated.
- No data repo mutation occurred.
- No DB write occurred.
- No scheduler activation occurred.
- No production warehouse mutation occurred.

## Next Gate

The next required gate is the quarantine download approval record.

