# Polygon Stock Day Agg 2026-06-16 Parse Normalize Handoff Approval Package

## Purpose

Request approval to parse and decompress the quarantined `2026-06-16` file locally, normalize records, generate handoff candidate artifacts, and generate an intake package for `ai-market-machine-data`.

## Evidence Basis

- Quarantine download evidence commit: `d4b4896`
- Local quarantine path: `outputs/quarantine/polygon_flat_files/polygon_stocks_day_aggs_2026-06-16.csv.gz`
- Size_bytes: `316221`
- Sha256: `9f40f8beb445623aa77f3a2f9fa721ae7f7fa99c27021df683bc8044f9f2b0a1`

## Approved Scope

- Local-only decompression and parse of the already quarantined file
- Normalize Polygon stock day aggregate rows
- Generate handoff candidate rows jsonl
- Generate summary json
- Generate batch manifest json
- Generate intake package json
- No vendor call
- No remote read
- No download
- No DB write
- No data repo mutation
- No scheduler/backfill
- No AI wiring

## Expected Output Paths for 2026-06-16

- `outputs/handoff_candidates/polygon_stock_day_aggs/polygon_stock_day_aggs_2026-06-16_rows.jsonl`
- `outputs/handoff_candidates/polygon_stock_day_aggs/polygon_stock_day_aggs_2026-06-16_summary.json`
- `outputs/handoff_candidates/polygon_stock_day_aggs/polygon_stock_day_aggs_batch_2026-06-16_2026-06-16_manifest.json`
- `outputs/intake_packages/polygon_stock_day_aggs/polygon_stock_day_aggs_2026-06-16_2026-06-16_intake_package.json`

## Approval Phrase

`APPROVE POLYGON STOCK DAY AGG 2026-06-16 PARSE NORMALIZE HANDOFF`

## Operator Approval Record Template

- Approval phrase
- Approver
- Date/time
- Input quarantine file
- Input sha256
- Expected output paths
- Scope
- Non-authorized actions
- Required post-execution evidence

## Required Post-Execution Evidence

- Command used
- Input file path
- Input file size and sha256
- Row count
- Symbol count
- Rejected row count
- Output paths
- Output file exists flags
- Output file sizes
- Output file hashes if practical
- No vendor call confirmation
- No download confirmation
- No DB write confirmation
- No data repo mutation confirmation
- No scheduler/backfill confirmation
- No AI wiring confirmation
- Secrets not printed
- Unrelated untracked files untouched
- Generated outputs left uncommitted unless separately approved

## Not Authorized

- Vendor call/listing/probe
- Remote file read
- Download
- DB write
- Data repo mutation
- Production staging load
- Canonical promotion
- Scheduler/backfill
- AI wiring
- Committing generated output artifacts
- Staging or deleting unrelated untracked files
- Printing secrets or DB URLs

## Next Step

- Create operator approval record
- After approval, execute parse, normalize, and handoff generation
- After handoff package exists, move to `ai-market-machine-data` intake validation approval

## Completion Statement

This package records approval intent only and does not execute parse, normalize, or handoff actions.
