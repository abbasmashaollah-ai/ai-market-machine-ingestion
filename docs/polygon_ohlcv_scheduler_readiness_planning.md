# Polygon OHLCV Scheduler Readiness Planning

`scripts/plan_polygon_ohlcv_scheduler_cycle.py` is a manual read-only planning command for future scheduler readiness.

## Scope

The command:

- accepts repeated `--symbol`
- defaults to `SPY`, `QQQ`, `IWM` when no symbol is supplied
- accepts `--as-of-date`
- accepts `--timeframe`, default `1d`
- accepts `--source`, default `polygon_aggregates`
- accepts `--max-requests`
- accepts `--chunk-days`, default 10
- accepts `--daily-window-days`, default 5
- accepts `--check-existing`
- uses the market calendar helper
- reuses daily update and backfill planning semantics
- classifies each symbol into an operator-friendly update mode
- prints a safe recommended manual command string only
- prints a safe aggregate scheduler-readiness summary

## Safety

The command does not:

- call Polygon
- require `POLYGON_API_KEY`
- write to the database
- create tables
- run migrations
- schedule work
- run automatically on Railway startup
- expose API routes
- add AI, trading, risk, signal, regime, portfolio, strategy, or prediction logic

It fails safely if `DATABASE_URL` is missing and `--check-existing` is supplied.

`ai-market-machine-data` remains the schema owner.
