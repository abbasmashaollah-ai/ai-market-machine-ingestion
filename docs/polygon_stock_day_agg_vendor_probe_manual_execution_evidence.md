# Polygon Stock Day Agg Manual Vendor Listing Probe Execution Evidence

## Purpose

Record manual operator-run vendor listing/probe evidence for `2026-06-16`.

## Execution Context

- Manual PowerShell session
- Codex environment did not inherit local environment
- Earlier Codex blocker commit: `406a827`
- This manual evidence supersedes the blocked Codex execution for environment-specific probe status

## Preconditions

- Readiness checker returned `readiness_passed true`
- Readiness checker returned `safe_to_retry_probe true`
- Required config key names were present
- Only key names were documented; no values

## Probe Command

`python scripts/preflight_polygon_flat_file_manifest.py --enable-remote-listing --start-date 2026-06-16 --end-date 2026-06-16 --max-days 1`

- Listing/probe-only
- No download flags
- No write flags
- No parse/normalization/handoff flags

## Probe Result

- `object_present true`
- Date: `2026-06-16`
- `redacted_key_tail 2026/06/2026-06-16.csv.gz`
- `remote_list_expected_filename 2026-06-16.csv.gz`
- `size_bytes 316221`
- `etag_present true`
- `last_modified_present true`
- `listed_key_sha256_prefix a988421953a6`
- `resolved_key_sha256_prefix a988421953a6`
- Outcome: `file_available_for_future_download_approval`

## Safety Confirmations

- `vendor_call_attempted true`
- `remote_object_list_attempted true`
- `remote_file_read_attempted false`
- `download_attempted false`
- `export_attempted false`
- `db_write_attempted false`
- `ingestion_attempted false`
- `scheduler_activation_attempted false`
- `production_mutation_attempted false`
- `production_handoff_generation_authorized false`
- `credentials_printed false`
- `bucket_value_printed false`
- `endpoint_value_printed false`
- `prefix_value_printed false`
- No secrets printed
- Unrelated untracked files were not staged or deleted

## Next Step

- Create a separate quarantine download approval package for the available `2026-06-16` file
- No download is authorized by this evidence
- No remote file read is authorized by this evidence
- No parse/normalization/handoff/intake generation is authorized by this evidence
- No data repo staging/canonical promotion is authorized by this evidence

## Not Authorized

- Download
- Quarantine write
- Parse/normalization
- Handoff generation
- Intake package generation
- DB write
- Data repo mutation
- Production staging load
- Canonical promotion
- Scheduler/backfill
- AI wiring
- Generated output commit
- Unrelated untracked file staging/deletion
- Secrets printed

## Completion Statement

This evidence records a successful manual probe result for `2026-06-16` and documents the available file without authorizing any follow-on download.
