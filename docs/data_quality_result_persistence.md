# Manual Data Quality Result Persistence

`app/state/data_quality_result_store.py` is the approved operational writer for manual quality outcomes.

## Behavior

- writes to `data_quality_results` only when the contract is present
- never creates tables
- never runs migrations
- never prints secrets
- fails safely with a sanitized error when the contract is unavailable

## Chunked Polygon backfill usage

`scripts/run_polygon_ohlcv_chunked_backfill.py` accepts `--record-quality`.

When enabled:

- `DATABASE_URL` is required
- a compact quality row is recorded after each processed chunk
- the record includes vendor, dataset, symbol, timeframe, check name, status, severity, message, and optional observed/expected values
- the record is a validation summary only; it does not alter canonical write behavior
- `--record-quality` can be used with `--record-run`, and the quality row may include `run_id`/`job_id` only if the live contract supports those columns

This repository still does not own the schema. `ai-market-machine-data` remains the schema owner.
