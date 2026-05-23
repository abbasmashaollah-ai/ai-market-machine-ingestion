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
- splits the date range into chunks and runs the existing manual Polygon OHLCV incremental runtime per symbol/chunk
- writes only through the approved OHLCV writer and checkpoint store when `--confirm-write` is supplied
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

`ai-market-machine-data` remains the schema owner.
