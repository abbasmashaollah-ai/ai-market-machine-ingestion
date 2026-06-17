# Polygon Stock Day Agg Batch Local Handoff Artifact Writer

This batch writer is local-only and non-production.

It scans a local quarantine directory or date range, finds local Polygon stock day aggregate gzip files, and reuses the single-date writer to write per-date local handoff artifacts plus a batch manifest.

Required approval phrase:

`APPROVE POLYGON STOCK DAY AGG LOCAL HANDOFF ARTIFACT WRITE`

Produced files:

- per-date summary JSON
- per-date rows JSONL
- one batch manifest JSON

Safety rules:

- no vendor calls
- no remote downloads
- no DB writes
- no ingestion
- no scheduler activation
- no production mutation
- no direct data-repo mutation
- no API route creation
- no warehouse DB writer creation
- no committing quarantine vendor data

Allowed output root:

`outputs/handoff_candidates/polygon_stock_day_aggs/`

The batch manifest records dates processed, dates missing, counts, per-date artifact paths, and the safety flags for the run.
The data-repo ingestion step remains separate and deferred.
