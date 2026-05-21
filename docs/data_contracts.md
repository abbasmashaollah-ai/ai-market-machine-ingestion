# Data Contracts

This repository documents approved table contracts at a high level only.

`ai-market-machine-ingestion` does not own canonical schema or migrations. `ai-market-machine-data` owns all canonical schema, table definitions, and schema evolution.

## Shared Rules

- Canonical schema ownership belongs to `ai-market-machine-data`.
- Ingestion may read approved tables as needed for operational flow.
- Ingestion may write only through approved writer modules.
- Canonical writes must be validated, reconciled, and lineage-tracked.
- Quality results must be recorded for meaningful ingestion outcomes.

## Table Contracts

### `symbol_master`

- Purpose: canonical symbol identity and mapping data.
- Schema owner: `ai-market-machine-data`.
- Ingestion read/write: ingestion may read; ingestion may write only through approved writers if that is part of the approved contract.
- Notes about usage: used to resolve vendor symbols to approved canonical identities.

### `canonical_ohlcv`

- Purpose: approved canonical OHLCV market data.
- Schema owner: `ai-market-machine-data`.
- Ingestion read/write: ingestion may read; ingestion may write only through approved writers and only for approved records.
- Notes about usage: this is a canonical output table, not an ingestion staging table.

Uniqueness rule:

- `symbol_id + timestamp + timeframe + adjusted`

Adjusted vs unadjusted rule:

- Adjusted and unadjusted records are distinct canonical variants.
- The `adjusted` flag must be explicit and preserved.

Timestamp/timezone rule:

- Timestamps must be treated consistently and recorded in a canonical timezone format.
- Ingestion must not rely on ambiguous local-time representations.

### `ingestion_jobs`

- Purpose: operational definitions for ingestion work.
- Schema owner: `ai-market-machine-data`.
- Ingestion read/write: ingestion may read and may write operational state through approved writers.
- Notes about usage: identifies what job should run, for which vendor/source, and under what operational settings.

### `ingestion_checkpoints`

- Purpose: resumable progress markers for incremental runs and backfills.
- Schema owner: `ai-market-machine-data`.
- Ingestion read/write: ingestion may read and may write through approved writers.
- Notes about usage: required for safe retries, restarts, and backfill resumption.

### `ingestion_runs`

- Purpose: run history and execution metadata.
- Schema owner: `ai-market-machine-data`.
- Ingestion read/write: ingestion may read and may write through approved writers.
- Notes about usage: records status, timing, and operational outcome for each run.

### `ingestion_errors`

- Purpose: structured error capture for failed or partially failed operations.
- Schema owner: `ai-market-machine-data`.
- Ingestion read/write: ingestion may read and may write through approved writers.
- Notes about usage: used for debugging, retry decisions, and operator visibility.

### `data_quality_results`

- Purpose: recorded quality checks and validation outcomes.
- Schema owner: `ai-market-machine-data`.
- Ingestion read/write: ingestion may read and may write through approved writers.
- Notes about usage: quality results must exist before approved canonical writes.

Quality result rule:

- Quality validation must occur before canonical writes.
- Failed quality checks must be retained as operational evidence and not silently ignored.

### `data_lineage`

- Purpose: source-to-canonical traceability for approved records.
- Schema owner: `ai-market-machine-data`.
- Ingestion read/write: ingestion may read and may write through approved writers.
- Notes about usage: every approved record must be traceable back to source inputs and processing context.

Lineage rule:

- Lineage is required for approved data and must be recorded as part of the ingestion flow.

## Summary Boundary

This repository documents and uses the approved data contract, but it does not own the schema, migrations, or canonical table lifecycle. That responsibility remains with `ai-market-machine-data`.
