# Market Feature Bundle Multi-Symbol Fixture Dry-Run Plan

## Purpose

- define fixture-only dry-run preparation for QQQ/IWM/DIA `market_feature_bundle` pilot expansion
- validate expansion shape before production writes
- unblock later AI Machine multi-symbol diagnostics only after certified evidence exists

## Scope

- target QQQ, IWM, and DIA
- SPY remains existing certified baseline
- fixture-only dry-run first
- no production writes
- no live API calls
- no vendor calls
- no scheduler activation

## Required fixture dry-run behavior

- generate or validate local fixture-shaped `market_feature_bundle` payloads only
- preserve `schema_version market_feature_bundle.v1`
- use `dataset_version production_pilot.fixture_dry_run.v1` or similar non-production label
- require `validation_status PASS` before any later approval
- require `coverage_status COMPLETE` in fixture dry-run outputs
- require `quality_status PASS` in fixture dry-run outputs
- mark `certification_status` as `DRY_RUN_CERTIFIED` or `FIXTURE_CERTIFIED`, not production `CERTIFIED`
- preserve lineage/evidence placeholders as fixture-only
- reject or mark `INSUFFICIENT_EVIDENCE` if fixture shape is incomplete

## Required checks before production approval

- compare fixture output shape against existing SPY pilot contract
- verify QQQ/IWM/DIA all have complete fixture sections
- verify no missing/stale evidence unless explicitly safe
- verify idempotency key behavior is deterministic and safe
- verify no secrets/tokens/raw provider credentials
- verify no DB writes or live calls occurred

## Post-dry-run decision gate

- manual approval required before any production seed/write
- production expansion can proceed only after fixture dry-run passes
- Data API precondition must be rechecked after any approved write
- AI Machine multi-symbol diagnostic remains blocked until QQQ/IWM/DIA are certified by Data API

## Forbidden actions

- no ingestion execution
- no DB writes
- no vendor calls
- no live API calls
- no production changes
- no scheduler activation
- no AI Machine runtime wiring
- no secrets committed

