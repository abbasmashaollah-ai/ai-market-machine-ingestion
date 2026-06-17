# Polygon Stock Day Agg Local Handoff Artifact Writer

This writer is local-only and non-production.

It reads the quarantined Polygon stock day aggregates gzip CSV, validates and normalizes rows, and writes handoff candidate artifacts only under the approved local output directory.

Required approval phrase:

`APPROVE POLYGON STOCK DAY AGG LOCAL HANDOFF ARTIFACT WRITE`

Allowed output directory:

`outputs/handoff_candidates/polygon_stock_day_aggs/`

Produced files:

- `polygon_stock_day_aggs_YYYY-MM-DD_summary.json`
- `polygon_stock_day_aggs_YYYY-MM-DD_rows.jsonl`

Safety flags and guarantees:

- no vendor calls
- no remote downloads
- no DB writes
- no ingestion activation
- no scheduler activation
- no production mutation
- no direct `ai-market-machine-data` mutation
- no API route creation
- no warehouse DB writer creation
- no committing quarantine vendor data
- safe JSON output only
- source file hash included
- record counts included

The writer is intended as the final local approval step before any future ai-market-machine-data ingestion work.
That future step remains separate and is not enabled by this writer.
