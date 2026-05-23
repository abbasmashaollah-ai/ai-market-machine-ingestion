# Polygon OHLCV Daily Update Planning

`scripts/plan_polygon_ohlcv_daily_update.py` is a manual read-only planner for a daily Polygon OHLCV update.

## Scope

The command:

- accepts repeated `--symbol`
- defaults to `SPY`, `QQQ`, `IWM` when no symbol is supplied
- accepts `--as-of-date`
- accepts `--timeframe`, default `1d`
- accepts `--source`, default `polygon_aggregates`
- accepts `--check-existing`
- uses the market calendar helper to identify the latest expected trading day on or before the as-of date
- reads `canonical_ohlcv` only when `--check-existing` is supplied and `DATABASE_URL` is present
- prints per-symbol planning details and an aggregate summary

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
