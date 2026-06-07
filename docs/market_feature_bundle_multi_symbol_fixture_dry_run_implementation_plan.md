# Market Feature Bundle Multi-Symbol Fixture Dry-Run Implementation Plan

## Purpose

- define how to build the QQQ/IWM/DIA fixture dry-run package
- prepare fixture validation before any production seed/write
- keep all work non-production and deterministic

## Planned fixture files

- `tests/fixtures/market_feature_bundle/qqq_fixture_dry_run.json`
- `tests/fixtures/market_feature_bundle/iwm_fixture_dry_run.json`
- `tests/fixtures/market_feature_bundle/dia_fixture_dry_run.json`
- optionally `tests/fixtures/market_feature_bundle/spy_contract_reference.json` if copied from the known SPY pilot shape

## Planned validator/test surfaces

- fixture schema validator helper or test-only validator
- tests/unit or tests/docs fixture contract tests
- no runtime writer integration
- no DB integration
- no scheduler integration

## Required fixture contract

- universe QQQ/IWM/DIA
- observation_date 2026-01-15 unless explicitly changed later
- schema_version market_feature_bundle.v1
- dataset_version production_pilot.fixture_dry_run.v1
- validation_status PASS
- coverage_status COMPLETE
- quality_status PASS
- certification_status FIXTURE_CERTIFIED or DRY_RUN_CERTIFIED
- source_repo ai-market-machine-ingestion
- source_run_id fixture_dry_run.v1
- lineage/evidence refs fixture-only
- no secrets/tokens/raw provider credentials
- deterministic idempotency_key or deterministic fixture idempotency placeholder

## Validation rules

- reject missing universe
- reject mismatched universe
- reject missing observation_date
- reject wrong schema_version
- reject production CERTIFIED status in fixture dry-run
- reject missing validation/coverage/quality status
- reject missing lineage/evidence placeholders unless explicitly safe
- reject raw credentials/secrets/tokens
- reject non-deterministic idempotency behavior

## Execution sequence after approval

- create fixture directory and fixture files
- create test-only fixture validator
- run tests only
- do not write to DB
- do not expose fixtures through Data API
- manual approval required before any production seed/write

## Forbidden actions

- no ingestion execution
- no DB writes
- no vendor calls
- no live API calls
- no production changes
- no scheduler activation
- no AI Machine runtime wiring
- no secrets committed
