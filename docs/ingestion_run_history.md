# Ingestion Run History

`app/state/ingestion_run_store.py` is the approved operational writer for manual ingestion run history.

## Behavior

- writes to `ingestion_runs` only when the contract is present
- writes to `ingestion_errors` only when the contract is present and errors are supplied
- never creates tables
- never runs migrations
- never prints secrets
- fails safely with sanitized errors when the contract is unavailable

## Current usage

`scripts/run_polygon_ohlcv_chunked_backfill.py` can record a run summary when `--record-run` is supplied.

Recorded metadata is intentionally compact:

- vendor
- dataset
- run status
- started and finished dates
- request budget values
- rate-limit outcome
- chunk stop outcome

The repository does not own the schema for these tables. `ai-market-machine-data` remains the schema owner.
