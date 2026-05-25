# Single-Symbol FMP OHLCV Ingestion Vertical Slice

This repository now contains the first production-oriented single-symbol FMP OHLCV ingestion slice.

## Ownership

`ai-market-machine-ingestion` owns:

- live FMP vendor fetching
- raw OHLCV normalization
- ingestion orchestration
- retry/error classification
- checkpoint planning
- lineage/evidence payload creation

`ai-market-machine-data` continues to own:

- schemas
- read APIs
- canonical contracts
- protected governance/evidence metadata
- read-only health/readiness surfaces

## Current slice behavior

The slice is intentionally dry-run/write-plan only for now.

It:

- accepts one symbol and a date range
- fetches FMP OHLCV rows through a testable vendor client
- normalizes rows into canonical-ready OHLCV records
- returns a deterministic write-plan payload
- sets `did_write_db: false`
- emits lineage/evidence metadata compatible with the data-side contract shape
- emits checkpoint plan metadata
- classifies vendor fetch failures narrowly

It does not:

- write to the database
- wire into scheduler or cron
- perform broad backfills
- introduce trading, regime, portfolio, or risk logic
- import `ai-market-machine-data`

## Compatibility shape

The returned plan includes:

- vendor
- symbol
- requested date range
- raw record count
- normalized record count
- intended target
- lineage evidence
- checkpoint plan
- errors
- `did_write_db: false`

## What is intentionally not implemented yet

- live canonical writes
- scheduler integration
- broad backfill orchestration
- checkpoint persistence
- sync-state persistence
- multi-symbol fan-out

## Next step before data-repo facade/deletion work

Before `ai-market-machine-data` can facade or delete its remaining `fmp_client.py` and `ohlcv_ingestor.py`, this slice must be extended into the live single-symbol execution path and callers must move over to this repo-owned implementation.
