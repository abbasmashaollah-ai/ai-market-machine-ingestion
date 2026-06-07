# Market Feature Bundle Multi-Symbol Production Seed Preparation Audit

## Purpose

- prepare controlled manual production seed/write for QQQ/IWM/DIA
- audit existing production pilot writer/runner paths before execution
- preserve safety before any DB write

## User approval scope

- approved preparation only
- no execution yet
- no scheduler activation
- no broad backfill
- no automated recurring job
- no AI Machine runtime wiring

## Current state

- SPY certified
- QQQ/IWM/DIA MISSING / WARN / UNCERTIFIED
- QQQ/IWM/DIA fixture dry-run payloads exist and validate
- fixture evidence is not production evidence
- AI Machine multi-symbol diagnostic remains blocked until Data API certification

## Search results

- `app/writers/market_feature_bundle_writer.py` contains the production writer and idempotency checks
- `app/writers/market_feature_bundle_db_adapter.py` contains the persistence adapter and cleanup helpers
- writer/persist path
- `scripts/run_market_feature_bundle_one_row_production_pilot.py` is the manual production pilot runner candidate
- manual runner
- `scripts/run_market_feature_bundle_production_pilot_dry_run.py` is the no-write dry-run runner candidate
- safest likely existing command or state if none exists
- `docs/market_feature_bundle_producer_contract.md` defines the certification/validation gate and deterministic payload shape
- `tests/fixtures/market_feature_bundle/fixture_validator.py` validates fixture-only payloads
- `tests/docs/test_market_feature_bundle_multi_symbol_fixture_payloads.py` proves fixture payloads exist and validate

## Candidate execution path

- safest likely existing command: `scripts/run_market_feature_bundle_one_row_production_pilot.py`
- if no safe no-write path is acceptable, inspect `scripts/run_market_feature_bundle_production_pilot_dry_run.py` first and keep execution blocked
- inspect before execution: payload shape, approval env vars, validation gate, idempotency handling, route verification, and rollback/no-op behavior
- required env vars without printing values: `AMM_PRODUCTION_PILOT_APPROVAL`, `AMM_PRODUCTION_PILOT_DATABASE_URL`, `AMM_PRODUCTION_PILOT_DATA_BASE_URL`, `AMM_PRODUCTION_PILOT_DATA_TOKEN`
- expected input symbols: `QQQ`, `IWM`, `DIA`
- expected observation date: `2026-01-15`
- observation_date `2026-01-15`
- expected dataset_version: `production_pilot.v1` or approved successor
- dataset_version `production_pilot.v1`
- idempotency behavior

## Required controls before actual execution

- explicit second approval required before DB write
- dry-run/no-write command must pass first if available
- validation_status `PASS` required
- coverage_status `COMPLETE` required
- quality_status `PASS` required
- certification_status `CERTIFIED` required only after production validation
- deterministic idempotency required
- rollback or no-op strategy required
- post-write direct Data API verification required

## Production pilot mechanics observed

- manual one-row-style write only
- no scheduler activation
- no broad backfill
- no automated recurring job
- no provider calls unless explicitly approved
- write only certified rows
- reject or mark `INSUFFICIENT_EVIDENCE` if validation fails
- keep audit/lineage evidence

## Post-write verification requirements

- direct Data API check for SPY/QQQ/IWM/DIA
- QQQ/IWM/DIA must show `coverage_status COMPLETE`
- QQQ/IWM/DIA must show `quality_status PASS`
- QQQ/IWM/DIA must show `certification_status CERTIFIED`
- missing evidence remains `INSUFFICIENT_EVIDENCE`, not failure or bearish signal
- AI Machine multi-symbol diagnostic can proceed only after verification passes

## Forbidden in this preparation step

- no ingestion execution
- no DB writes
- no vendor calls
- no live API calls
- no production changes
- no scheduler activation
- no AI Machine runtime wiring
- no secrets committed

## Recommended next step

- if a safe dry-run/no-write path exists, run dry-run next after user approval
- if no safe path exists, create a dry-run-only manual seed command first
- still no DB write until explicit second approval
