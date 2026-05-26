# OHLCV Scheduler Contract

This document defines the scheduler contract for OHLCV operations in `ai-market-machine-ingestion`.

## Responsibilities

The scheduler contract is limited to FMP daily OHLCV scheduling intent. It may plan a daily FMP run, but it does not activate a scheduler in this repository.

The production ingestion path remains in manual/operator-run commands until explicit activation is introduced later.

## Non-responsibilities

This repository does not:

- start a scheduler
- own Railway startup behavior for scheduled ingestion
- own FastAPI routes
- own migrations or schema creation
- own AI/trading/risk/signal/regime/portfolio logic
- own `ai-market-machine-data`

## FMP daily update scope

The scheduler contract currently covers the FMP daily OHLCV path only.

The planned FMP run should reference:

- `scripts.run_fmp_ohlcv_daily_update`
- `scripts.preflight_fmp_ohlcv_operations`
- `scripts.verify_fmp_ohlcv_evidence_chain`

The plan must keep `schedule_allowed=false` until an explicit activation step is introduced.

## Polygon backfill remains manual

Polygon OHLCV backfill remains manual/operator-run.

The scheduler contract must not imply that Polygon backfill has scheduled ownership. Polygon should continue to use manual backfill and verification commands only.

## Preflight requirement

Any future scheduled run must be preceded by a successful preflight command.

For FMP, the preflight command is:

`python -m scripts.preflight_fmp_ohlcv_operations`

## Evidence verification requirement

Any future scheduled run must be followed by a read-only evidence verification command.

For FMP, the verifier is:

`python -m scripts.verify_fmp_ohlcv_evidence_chain`

## Expected flags

Scheduled FMP runs are expected to make the record intent explicit:

- `--confirm-write`
- `--record-run`
- `--record-quality`
- `--record-lineage`

The plan layer may describe these flags, but it does not execute them.

## Failure behavior

The scheduler plan must fail safely when:

- required manual command inventory is incomplete
- forbidden imports appear in manual command paths
- a scheduler activation file appears too early
- Railway startup points at a scheduler command

The scheduler plan must not call vendors or write to the database.

## Environment requirements

The scheduler plan must document required environment expectations for the planned command:

- `FMP_API_KEY` for live or confirm-write FMP behavior
- `DATABASE_URL` only when evidence or write recording is requested

## Railway / startup constraints

Railway startup remains scheduler-free.

The deployment entrypoint is still a placeholder health-style command, not a scheduler launcher.

The scheduler plan must report `schedule_allowed=false` until an explicit activation path exists and is approved separately.
