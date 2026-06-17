# Polygon Stock Day Agg Vendor Listing Probe Evidence

This document is evidence only.
It does not grant approval.
It does not execute production.

## Approval Reference

- Approval record path: `docs/approvals/polygon_stock_day_agg_vendor_listing_probe_approval_record.md`
- Approval phrase used: `APPROVE POLYGON STOCK DAY AGG VENDOR LISTING PROBE`
- Target gate: `vendor_listing_probe`
- Date probed: `2026-06-15`

## Probe Command

The smallest existing listing/preflight command used was:

`python scripts/preflight_polygon_flat_file_manifest.py --enable-remote-listing --start-date 2026-06-15 --end-date 2026-06-15 --max-days 1`

## Metadata-Only Result

The probe remained metadata-only and did not download object bytes.

The local run was blocked safely before any remote listing because Polygon flat-file configuration and `boto3` were not available in the current environment.

Observed local result:

- `config_classification: missing`
- `credentials_present: false`
- `vendor_call_attempted: false`
- `remote_object_list_attempted: false`
- `download_attempted: false`
- `remote_list_object_count_seen: 0`
- `remote_list_csv_gz_object_count_seen: 0`
- `manifest_entries: []`

## Endpoint / Bucket / Prefix Names Only

The probe command is designed to use Polygon flat-file listing metadata only.

No secrets were printed.

No endpoint, bucket, or prefix secret values were printed.

## Object / Key Presence Result

No object presence result was returned because the remote listing did not run in this environment.

The expected metadata-only key tail for the approved date was:

- `2026/06/2026-06-15.csv.gz`

The expected filename was:

- `2026-06-15.csv.gz`

## No Side Effects

- No download
- No quarantine artifact generated
- No handoff artifact generated
- No data repo mutation
- No DB write
- No scheduler activation
- No secrets printed

## Next Gate

The next gate required is quarantine download approval.

## Safety Note

This evidence records a safe blocked metadata-only probe attempt and does not authorize any later gate.

