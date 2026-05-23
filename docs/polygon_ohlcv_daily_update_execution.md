# Polygon OHLCV Daily Update Execution

`scripts/run_polygon_ohlcv_daily_update.py` is a manual operator command for running a tiny daily Polygon OHLCV update.

## Scope

The command:

- accepts repeated `--symbol`
- defaults to `SPY`, `QQQ`, `IWM` when no symbol is supplied
- accepts `--as-of-date`
- accepts `--timeframe`, default `1d`
- accepts `--source`, default `polygon_aggregates`
- accepts `--confirm-write`
- accepts `--record-run`
- accepts `--record-quality`
- accepts `--record-lineage`
- accepts `--check-existing`
- accepts `--max-requests`
- accepts `--allow-over-budget`
- accepts `--sleep-seconds-between-symbols`
- uses the daily-update planner logic to determine the needed update window
- skips symbols that are already up to date or have no expected trading day
- runs the existing Polygon OHLCV incremental runtime for symbols that need an update
- writes only through the approved writer and checkpoint path when `--confirm-write` is supplied

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

It fails safely before confirmed writes if `DATABASE_URL` is missing.
It fails safely before existing-data checks if `DATABASE_URL` is missing and `--check-existing` is supplied.

`ai-market-machine-data` remains the schema owner.
