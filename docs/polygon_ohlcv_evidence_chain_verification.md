# Polygon OHLCV Evidence Chain Verification

`scripts/verify_polygon_ohlcv_evidence_chain.py` is a manual read-only operator command for checking the evidence chain around a Polygon OHLCV symbol/window.

## Scope

The command:

- requires `DATABASE_URL`
- accepts `--symbol`
- accepts `--start-date`
- accepts `--end-date`
- accepts `--timeframe`
- accepts `--limit` for operational records, default 3
- reads `canonical_ohlcv`
- reads `ingestion_runs`
- reads `data_quality_results`
- reads `data_lineage`
- prints a safe summary of row count, coverage, run status, quality status, lineage status, and evidence state

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

It fails safely if `DATABASE_URL` is missing and never prints connection secrets.

`ai-market-machine-data` remains the schema owner.
