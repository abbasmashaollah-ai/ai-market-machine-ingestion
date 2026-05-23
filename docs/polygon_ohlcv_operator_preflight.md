# Polygon OHLCV Operator Preflight

`scripts/preflight_polygon_ohlcv_operations.py` is a manual read-only operator command for checking readiness before future daily automation or larger backfills.

## Scope

The command combines:

- symbol universe readiness
- daily update readiness
- request-budget readiness
- evidence-chain readiness

It accepts repeated `--symbol`, defaults to `SPY`, `QQQ`, `IWM`, and can optionally inspect existing canonical data when `--check-existing` is supplied.

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
