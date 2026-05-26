# Polygon OHLCV Evidence Chain Verification

`scripts/verify_polygon_ohlcv_evidence_chain.py` is a manual read-only operator command for checking the evidence chain around a Polygon OHLCV symbol/window.

## Scope

The command:

- requires `DATABASE_URL`
- accepts `--symbol`
- accepts `--start-date`
- accepts `--end-date`
- accepts `--timeframe`
- accepts `--chunk-days` for backfill checkpoint verification
- accepts `--confirmed-write`
- accepts `--record-run`
- accepts `--record-quality`
- accepts `--record-lineage`
- accepts `--resume-from-checkpoint`
- accepts `--limit` for operational records, default 3
- reads `canonical_ohlcv`
- reads `ingestion_runs`
- reads `data_quality_results`
- reads `data_lineage`
- reads `ingestion_checkpoints` when checkpoint verification is requested
- prints a safe summary of row count, coverage, run status, quality status, lineage status, and evidence state

Evidence lookups are explicit:

- exact match uses the selected symbol, timeframe, and date window when the table can support it
- fallback match uses vendor/dataset plus symbol/timeframe when date-window metadata is not enough to recover the recorded evidence
- the command prints `run_match_mode`, `quality_match_mode`, and `lineage_match_mode` as `exact`, `fallback`, or `none`
- `canonical_status`, `run_status`, `quality_status`, `lineage_status`, and `checkpoint_status` are printed as `PASS`, `WARN`, or `FAIL`
- `evidence_status` is `PASS` when all required checks pass, `WARN` when optional evidence is present without being requested, and `FAIL` when any required check fails
- `--confirmed-write` requires canonical rows for the inspected window
- `--record-run` requires run history rows for the inspected window
- `--record-quality` requires quality rows for the inspected window
- `--record-lineage` requires lineage rows for the inspected window
- `--resume-from-checkpoint` requires checkpoint rows for each planned chunk and fails when a chunk checkpoint is missing or stale

The core PASS/WARN/FAIL semantics are shared with the FMP evidence verifier through `scripts.evidence_chain_helpers`.

## Verification Log

Live evidence-chain verification:

`python -m scripts.verify_polygon_ohlcv_evidence_chain --symbol SPY --start-date 2025-01-02 --end-date 2025-01-10 --timeframe 1d --confirmed-write --record-run --record-quality --record-lineage --resume-from-checkpoint --chunk-days 10`

Output:

- `symbol=SPY`
- `timeframe=1d`
- `row_count=12`
- `coverage_ratio=1.000`
- `missing_dates=[]`
- `latest_run_status=success`
- `run_match_mode=fallback`
- `run_status=PASS`
- `quality_results_count=1`
- `latest_quality_status=pass`
- `quality_match_mode=fallback`
- `quality_status=PASS`
- `lineage_rows_count=1`
- `latest_lineage_quality_status=pass`
- `lineage_match_mode=fallback`
- `lineage_status=PASS`
- `checkpoint_rows_count=1`
- `checkpoint_expected_chunks=1`
- `checkpoint_failures=0`
- `checkpoint_status=PASS`
- `canonical_status=PASS`
- `evidence_status=PASS`

Dry-run verification:

`python -m scripts.verify_polygon_ohlcv_evidence_chain --symbol SPY --start-date 2025-01-10 --end-date 2025-01-14 --timeframe 1d`

SPY output:

- `row_count=4`
- `coverage_ratio=1.000`
- `missing_dates=[]`
- `canonical_status=PASS`
- `run_status=PASS`
- `quality_status=PASS`
- `lineage_status=PASS`
- `checkpoint_status=PASS`
- `evidence_status=PASS`

`python -m scripts.verify_polygon_ohlcv_evidence_chain --symbol QQQ --start-date 2025-01-10 --end-date 2025-01-14 --timeframe 1d --record-quality`

QQQ output:

- `row_count=4`
- `coverage_ratio=1.000`
- `missing_dates=[]`
- `quality_status=FAIL`
- `lineage_status=PASS`
- `evidence_status=FAIL`

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
