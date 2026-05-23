# Manual Polygon OHLCV Tiny Universe Check

`scripts/run_polygon_ohlcv_tiny_universe_check.py` is a manual operator command for verifying a small Polygon OHLCV universe before larger backfills.

## Scope

The command:

- accepts repeated `--symbol`
- defaults to `SPY`, `QQQ`, `IWM` when no symbol is supplied
- accepts `--start-date`
- accepts `--end-date`
- accepts `--timeframe`
- accepts `--confirm-write`
- reuses the existing manual Polygon OHLCV incremental runtime
- writes only through the approved OHLCV writer and checkpoint store when `--confirm-write` is supplied
- prints one safe summary line per symbol
- prints an aggregate summary line with:
  - `symbols_total`
  - `symbols_completed`
  - `symbols_failed`
  - `symbols_skipped`
  - `total_rows_fetched`
  - `total_rows_written`
  - `symbols_with_full_coverage`
  - `symbols_with_gaps`

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

If `DATABASE_URL` is unavailable, the command skips checkpoint and coverage sections safely.

`ai-market-machine-data` remains the schema owner.
