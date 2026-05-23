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

## Verification Log

Live command:

`python -m scripts.run_polygon_ohlcv_chunked_backfill --symbol SPY --start-date 2025-01-02 --end-date 2025-01-10 --timeframe 1d --chunk-days 10 --max-requests 3 --record-lineage`

Result:

- `symbol=SPY`
- `rows_fetched=6`
- `rows_written=0`
- `write_confirmed=false`
- `status=completed`
- `request_budget_status=within_budget`
- `estimated_vendor_requests=1`
- `max_requests=3`

Inspection:

`python -m scripts.inspect_data_lineage --vendor polygon --dataset ohlcv --limit 3`

Returned:

- `vendor=polygon`
- `dataset=ohlcv`
- `symbol=SPY`
- `timeframe=1d`
- `source_endpoint=v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from}/{to}`
- `response_status=200`
- `row_count=6`
- `normalization_version=polygon_ohlcv_normalization_v1`
- `quality_status=pass`
- `rows_returned=1`

`ai-market-machine-data` remains the schema owner.
