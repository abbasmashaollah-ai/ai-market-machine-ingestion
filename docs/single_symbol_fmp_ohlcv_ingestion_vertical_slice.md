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
- controlled multi-symbol fan-out reuse

`ai-market-machine-data` continues to own:

- schemas
- read APIs
- canonical contracts
- protected governance/evidence metadata
- read-only health/readiness surfaces

## Current slice behavior

The slice is intentionally dry-run/write-plan by default.

It:

- accepts one symbol and a date range
- fetches FMP OHLCV rows through a testable vendor client
- normalizes rows into canonical-ready OHLCV records
- returns a deterministic write-plan payload
- sets `did_write_db: false`
- computes a writer-handoff preview for `canonical_ohlcv`
- emits lineage/evidence metadata compatible with the data-side contract shape
- emits checkpoint plan metadata
- classifies vendor fetch failures narrowly
- can optionally execute an injected writer in tests or controlled integration scenarios
- can optionally execute an injected checkpoint writer in tests or controlled integration scenarios

It does not:

- write to the database
- wire into scheduler or cron
- perform broad backfills
- introduce trading, regime, portfolio, or risk logic
- import `ai-market-machine-data`

The single-symbol orchestrator remains the reusable execution unit for the new multi-symbol fan-out layer. That fan-out layer lives in this repository, keeps dry-run defaults, and aggregates one single-symbol plan per requested symbol.

## Compatibility shape

The returned plan includes:

- vendor
- symbol
- requested date range
- raw record count
- normalized record count
- intended target
- intended writer target
- writer handoff readiness
- writer payload preview
- writer execution requested
- writer execution performed
- writer result
- writer errors
- checkpoint persistence requested
- checkpoint persistence performed
- checkpoint result
- checkpoint errors
- lineage evidence
- checkpoint plan
- errors
- `did_write_db: false`

## What is intentionally not implemented yet

- live canonical writes
- live writer execution
- scheduler integration
- broad backfill orchestration
- checkpoint persistence
- sync-state persistence
- ai-market-machine-data imports

## Writer handoff contract

The orchestrator now produces a writer-ready preview for `app/writers/ohlcv_writer.py` without invoking the writer.
When writer execution is explicitly enabled, the orchestrator passes `list[NormalizedOHLCVRecord]` directly into `OhlcvWriter.write()`.

The preview is only a contract artifact and includes:

- `symbol`
- `timestamp`
- `open`
- `high`
- `low`
- `close`
- `volume`
- `source`
- `adjustment_status`
- `data_quality_status`
- `timeframe`
- `adjusted`

The slice validates that these fields are present before declaring `writer_handoff_ready: true`.

## Writer execution interface

The orchestrator accepts an explicit writer execution mode.

Default behavior:

- `writer_execution_requested: false`
- `writer_execution_performed: false`
- `did_write_db: false`
- `writer_result: null`
- `writer_errors: ()`

Injected writer mode:

- a caller passes a writer object or callable
- the caller sets `execute_writer: true`
- the orchestrator sends the writer-ready payload to the injected writer
- `writer_result` captures the writer response in a plain dictionary
- `writer_errors` captures any explicit writer failure or exception
- `did_write_db` becomes `true` only when the injected writer explicitly reports success

This is a controlled integration hook for testing and future staged enablement.

## Checkpoint persistence interface

The orchestrator also exposes an explicit checkpoint persistence mode.

Default behavior:

- `checkpoint_persistence_requested: false`
- `checkpoint_persistence_performed: false`
- `checkpoint_result: null`
- `checkpoint_errors: ()`

Injected checkpoint mode:

- a caller passes a checkpoint writer object or callable
- the caller sets `execute_checkpoint_persistence: true`
- the orchestrator sends the checkpoint plan payload to the injected checkpoint writer
- `checkpoint_result` captures the checkpoint writer response in a plain dictionary
- `checkpoint_errors` captures any explicit checkpoint failure or exception
- checkpoint persistence failures do not make the run look successful

This is a controlled integration hook for testing and future staged enablement. It keeps checkpoint persistence disabled by default.

## Why DB writes remain disabled

The writer layer in this repository expects a database connection and writes directly to `canonical_ohlcv`.
For this first slice, the integration remains dry-run only so the repo can prove fetch, normalization, and write planning without enabling live persistence by default.

## Next step before data-repo facade/deletion work

Before `ai-market-machine-data` can facade or delete its remaining `fmp_client.py` and `ohlcv_ingestor.py`, the live single-symbol execution path must be moved over and the data repo callers must switch to the ingestion-owned implementation.
