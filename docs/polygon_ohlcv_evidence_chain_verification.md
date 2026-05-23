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

Evidence lookups are explicit:

- exact match uses the selected symbol, timeframe, and date window when the table can support it
- fallback match uses vendor/dataset plus symbol/timeframe when date-window metadata is not enough to recover the recorded evidence
- the command prints `run_match_mode`, `quality_match_mode`, and `lineage_match_mode` as `exact`, `fallback`, or `none`
- `evidence_status` is `complete` when canonical coverage is complete and all three evidence types are present, `partial` when canonical coverage is complete but only some evidence types are present, `missing` when canonical rows exist but no evidence exists, and `no_data` when canonical rows are missing

## Verification Log

Live evidence-chain verification:

`python -m scripts.verify_polygon_ohlcv_evidence_chain --symbol SPY --start-date 2025-01-02 --end-date 2025-01-10 --timeframe 1d`

Output:

- `symbol=SPY`
- `timeframe=1d`
- `row_count=12`
- `coverage_ratio=1.000`
- `missing_dates=[]`
- `latest_run_status=success`
- `run_match_mode=fallback`
- `quality_results_count=1`
- `latest_quality_status=pass`
- `quality_match_mode=fallback`
- `lineage_rows_count=1`
- `latest_lineage_quality_status=pass`
- `lineage_match_mode=fallback`
- `evidence_status=complete`

`python -m scripts.verify_polygon_ohlcv_evidence_chain --symbol SPY --start-date 2025-01-10 --end-date 2025-01-14 --timeframe 1d`

SPY output:

- `row_count=4`
- `coverage_ratio=1.000`
- `missing_dates=[]`
- `latest_run_status=success`
- `run_match_mode=fallback`
- `quality_results_count=2`
- `latest_quality_status=pass`
- `quality_match_mode=fallback`
- `lineage_rows_count=2`
- `latest_lineage_quality_status=pass`
- `lineage_match_mode=fallback`
- `evidence_status=complete`

`python -m scripts.verify_polygon_ohlcv_evidence_chain --symbol QQQ --start-date 2025-01-10 --end-date 2025-01-14 --timeframe 1d`

QQQ output:

- `row_count=4`
- `coverage_ratio=1.000`
- `missing_dates=[]`
- `latest_run_status=success`
- `run_match_mode=fallback`
- `quality_results_count=1`
- `latest_quality_status=pass`
- `quality_match_mode=fallback`
- `lineage_rows_count=1`
- `latest_lineage_quality_status=pass`
- `lineage_match_mode=fallback`
- `evidence_status=complete`

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
