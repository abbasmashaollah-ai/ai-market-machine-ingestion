# FMP OHLCV Evidence Chain Verification

`scripts/verify_fmp_ohlcv_evidence_chain.py` is the read-only evidence verifier for manual FMP daily OHLCV updates.

## Scope

The verifier:

- requires `DATABASE_URL`
- accepts `--symbol`
- accepts `--start-date`
- accepts `--end-date`
- accepts `--timeframe`
- accepts `--confirmed-write`
- accepts `--record-run`
- accepts `--record-quality`
- accepts `--record-lineage`
- accepts `--limit`
- reads `canonical_ohlcv`
- reads `ingestion_runs`
- reads `data_quality_results`
- reads `data_lineage`
- prints compact evidence status for the inspected window

## Status model

The verifier reports explicit `PASS`, `WARN`, or `FAIL` statuses for:

- `canonical_status`
- `run_status`
- `quality_status`
- `lineage_status`
- `evidence_status`

## Contract

- `--confirmed-write` requires canonical rows for the inspected window
- `--record-run` requires run history rows for the inspected window
- `--record-quality` requires quality rows for the inspected window
- `--record-lineage` requires lineage rows for the inspected window
- when a check is not requested, the presence of that evidence produces `WARN`
- when a check is not requested and the evidence is absent, the verifier remains `PASS`

The core PASS/WARN/FAIL semantics are shared with the Polygon evidence verifier through `scripts.evidence_chain_helpers`.

## Safety

The verifier does not:

- call FMP
- write to the database
- create tables
- run migrations
- schedule work
- expose API routes
- add AI, trading, risk, signal, regime, portfolio, strategy, or prediction logic

It fails safely if `DATABASE_URL` is missing and never prints connection secrets.

`ai-market-machine-data` remains the schema owner.
