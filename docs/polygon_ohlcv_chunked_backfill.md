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

`ai-market-machine-data` remains the schema owner.
