# Manual Polygon OHLCV Chunked Backfill

`scripts/run_polygon_ohlcv_chunked_backfill.py` is a manual operator command for running a tiny, chunked Polygon OHLCV backfill.

## Scope

The command:

- accepts repeated `--symbol`
- defaults to `SPY`, `QQQ`, `IWM` when no symbol is supplied
- accepts `--start-date`
- accepts `--end-date`
- accepts `--timeframe`
- accepts `--chunk-days`
- accepts `--confirm-write`
- accepts conservative `--max-symbols` and `--max-chunks` caps
- accepts `--sleep-seconds-between-chunks`
- accepts `--stop-on-rate-limit` / `--no-stop-on-rate-limit`
- accepts `--max-rate-limit-failures`
- accepts `--dry-run-no-sleep`
- accepts `--max-requests`
- accepts `--allow-over-budget`
- accepts `--record-run`
- accepts `--record-quality`
- splits the date range into chunks and runs the existing manual Polygon OHLCV incremental runtime per symbol/chunk
- writes only through the approved OHLCV writer and checkpoint store when `--confirm-write` is supplied
- records an operational run summary through the approved ingestion run store when `--record-run` is supplied and the contract is available
- records compact quality outcomes through the approved quality result store when `--record-quality` is supplied and the contract is available
- prints one safe summary line per chunk
- prints one aggregate summary line

## Safety

The command does not:

- create tables
- run migrations
- expose API routes
- start a scheduler
- run automatically on Railway startup
- print `POLYGON_API_KEY`
- print `DATABASE_URL`
- add AI, trading, risk, signal, regime, portfolio, strategy, or prediction logic

It fails safely before execution if `POLYGON_API_KEY` is missing, and it fails safely before confirmed writes if `DATABASE_URL` is missing.
It also fails safely before run-history recording if `DATABASE_URL` is missing and `--record-run` is supplied.
It also fails safely before quality-result recording if `DATABASE_URL` is missing and `--record-quality` is supplied.

If the estimated vendor request count exceeds `--max-requests`, the runner blocks before any vendor call unless `--allow-over-budget` is supplied. In override mode, it continues but labels the request budget status as `override`.

When a chunk reports a sanitized 429 or rate-limit failure, the runner can stop remaining chunks immediately, or continue until the configured `--max-rate-limit-failures` threshold is reached. Sleeping between chunks is enabled by default and can be disabled for tests with `--dry-run-no-sleep`.

If `--record-run` is supplied, the runner stores a single summary row in `ingestion_runs` after execution and records any chunk-level errors in `ingestion_errors` when that contract is available. Over-budget blocks are recorded as `status=blocked_over_budget` when run history recording is enabled.

If `--record-quality` is supplied, the runner stores one compact quality summary row per processed chunk in `data_quality_results` when that contract is available. The quality row is informational and does not change whether the canonical writer is used or whether a chunk is accepted. If `--record-run` is also supplied, the quality row may include `run_id` and `job_id` when those columns exist.

If `--record-lineage` is supplied, the runner stores one compact lineage row per processed chunk in `data_lineage` when that contract is available. The lineage row is informational and does not change whether the canonical writer is used or whether a chunk is accepted. If `--record-run` is also supplied, the lineage row may include `run_id` and `job_id` when those columns exist.

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

Evidence-chain verification:

`python -m scripts.verify_polygon_ohlcv_evidence_chain --symbol SPY --start-date 2025-01-02 --end-date 2025-01-10 --timeframe 1d`

Returned:

- `symbol=SPY`
- `timeframe=1d`
- `row_count=12`
- `coverage_ratio=1.000`
- `missing_dates=[]`
- `latest_run_status=success`
- `run_match_mode=fallback`
- `quality_results_count=1`
- `latest_quality_status=pass`
- `quality_match_mode=fallback`
- `lineage_rows_count=1`
- `latest_lineage_quality_status=pass`
- `lineage_match_mode=fallback`
- `evidence_status=complete`

`ai-market-machine-data` remains the schema owner.
