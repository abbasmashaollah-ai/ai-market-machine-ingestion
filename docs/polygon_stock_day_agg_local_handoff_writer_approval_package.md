# Polygon Stock Day Agg Local Handoff Writer Approval Package

This document is an approval gate and does not execute anything.
It does not grant production approval by itself.

The next allowed implementation step, once explicitly approved, is a local-only handoff artifact writer that:

- reads the local quarantined gzip CSV
- validates and normalizes rows in memory
- writes a local preview or approved handoff artifact under an explicit non-production output path
- includes metadata, source file SHA256, source file size, requested date, row counts, rejection counts, and dataset/source fields

Required approval phrase for the later writer:

`APPROVE POLYGON STOCK DAY AGG LOCAL HANDOFF ARTIFACT WRITE`

Hard forbidden actions:

- vendor calls
- remote downloads
- DB writes
- production mutation
- scheduler activation
- direct ai-market-machine-data repo mutation
- API route creation
- warehouse writer creation
- ingestion activation
- committing quarantine vendor data

Allowed output location for the later local artifact only:

`outputs/handoff_candidates/polygon_stock_day_aggs/`

Expected artifact type for the later writer:

- JSONL, or
- a JSON summary plus JSONL rows

The approval package does not force the final artifact shape if a later implementation chooses a compatible local-only format.

Safety expectations for the later writer:

- explicit approval flag required
- explicit approval phrase required
- safe JSON output
- no secrets printed
- no full object keys printed
- source file hash included
- record counts included
- no DB credentials required

Required tests for the later writer:

- default no-approval blocks
- wrong approval phrase blocks
- approved local fixture writes only a local artifact
- malformed rows rejected safely
- no vendor, download, DB, scheduler, or production flags are true
- quarantine file is never committed

Next step after approval:

- implement the local-only handoff artifact writer under the allowed output path
- still no DB writes or production mutation
