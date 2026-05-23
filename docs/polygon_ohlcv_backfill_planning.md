# Manual Polygon OHLCV Backfill Planning

`scripts/plan_polygon_ohlcv_backfill.py` is a manual read-only operator command for estimating small-universe Polygon OHLCV backfill work before larger historical runs.

## Scope

The command:

- accepts repeated `--symbol`
- defaults to `SPY`, `QQQ`, `IWM` when no symbol is supplied
- accepts `--start-date`
- accepts `--end-date`
- accepts `--timeframe`
- uses the market calendar helper to compute expected trading days
- can optionally read existing `canonical_ohlcv` coverage when `--check-existing` is passed and `DATABASE_URL` is present
- supports optional `--source` and `--adjusted true|false|all` filters for existing coverage checks
- prints safe planning summaries only
- never calls Polygon
- never writes to the database

## Output

The command prints:

- `symbols_total`
- `timeframe`
- `start_date`
- `end_date`
- `expected_trading_days`
- `estimated_vendor_requests`
- `per_symbol_expected_rows`
- `per_symbol_existing_dates` when `--check-existing` is active and the database is available
- `per_symbol_missing_rows` when `--check-existing` is active and the database is available
- `per_symbol_missing_dates` when `--check-existing` is active and the database is available
- `total_expected_rows`
- `total_missing_rows` when `--check-existing` is active and the database is available

## Existing Coverage Semantics

When `--check-existing` is active:

- if `--source` is omitted, any source counts for a symbol/date/timeframe
- if `--source` is provided, only that source counts
- if `--adjusted all` is used, either adjusted variant counts
- if `--adjusted true` is used, only `adjusted=true` counts
- if `--adjusted false` is used, only `adjusted=false` counts

The command uses the same exclusive end-date convention and market calendar helper as the coverage diagnostics.

## Safety

The command does not:

- require `POLYGON_API_KEY`
- print `DATABASE_URL`
- create tables
- run migrations
- start a scheduler
- run automatically on Railway startup
- expose API routes
- add AI, trading, risk, signal, regime, portfolio, strategy, or prediction logic

`ai-market-machine-data` remains the schema owner.
