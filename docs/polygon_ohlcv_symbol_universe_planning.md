# Polygon OHLCV Symbol Universe Planning

`scripts/plan_polygon_ohlcv_symbol_universe.py` is a manual read-only planner for selecting and inspecting a tiny Polygon OHLCV symbol universe.

## Scope

The command:

- accepts repeated `--symbol`
- defaults to `SPY`, `QQQ`, `IWM` when no symbol is supplied
- accepts `--max-symbols`, default 25
- accepts `--universe-name`, default `manual_tiny_universe`
- accepts `--timeframe`, default `1d`
- accepts `--check-existing`
- reads canonical data only when `--check-existing` is supplied and `DATABASE_URL` is present
- prints per-symbol symbol-selection status
- prints an aggregate universe readiness summary

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
