# Manual Data Lineage Persistence

`app/state/data_lineage_store.py` is the approved operational writer for manual OHLCV lineage rows.

## Behavior

- writes to `data_lineage` only when the contract is present
- never creates tables
- never runs migrations
- never prints secrets
- fails safely with a sanitized error when the contract is unavailable

## Chunked Polygon backfill usage

`scripts/run_polygon_ohlcv_chunked_backfill.py` accepts `--record-lineage`.

When enabled:

- `DATABASE_URL` is required
- one compact lineage row is recorded after each processed chunk
- the row includes vendor, dataset, symbol, timeframe, source endpoint when available, request parameters, response status, row count, normalization version when available, and quality status when available
- `run_id` and `job_id` are included only if the live `data_lineage` contract supports those columns
- lineage persistence is informational and does not alter canonical write behavior
- `--record-lineage` can be used with `--record-run` and `--record-quality`

`ai-market-machine-data` remains the schema owner.
