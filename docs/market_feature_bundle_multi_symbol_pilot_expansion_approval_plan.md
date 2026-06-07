# Market Feature Bundle Multi-Symbol Pilot Expansion Approval Plan

This plan covers market_feature_bundle certified pilot evidence expansion.

## Purpose

- expand certified `market_feature_bundle` pilot evidence beyond SPY
- target QQQ, IWM, and DIA
- unblock the AI Machine multi-symbol diagnostic precondition

## Current Data API precondition result

- SPY: `coverage_status COMPLETE`, `quality_status PASS`, `certification_status CERTIFIED`
- QQQ: `coverage_status MISSING`, `quality_status WARN`, `certification_status UNCERTIFIED`
- IWM: `coverage_status MISSING`, `quality_status WARN`, `certification_status UNCERTIFIED`
- DIA: `coverage_status MISSING`, `quality_status WARN`, `certification_status UNCERTIFIED`

## Required approval before execution

- manual approval required before any ingestion/write/backfill
- no automatic production writes
- no scheduler activation
- no vendor calls until explicitly approved
- no AI Machine runtime wiring

## Candidate execution options

- fixture/dry-run only first
- manual one-row-style pilot expansion if approved
- reuse existing `market_feature_bundle` production pilot process
- preserve validation/certification gates
- write only certified rows
- reject or mark insufficient evidence if validation fails

## Required certification gates

- `coverage_status COMPLETE`
- `quality_status PASS`
- `certification_status CERTIFIED`
- `validation_status PASS`
- `schema_version market_feature_bundle.v1`
- `dataset_version production_pilot.v1` or explicitly versioned successor
- lineage/evidence references preserved
- no missing/stale evidence unless explicitly safe

## Post-expansion verification

- direct Data API check for SPY/QQQ/IWM/DIA
- AI Machine multi-symbol diagnostic can proceed only after QQQ/IWM/DIA are certified
- missing evidence must remain `INSUFFICIENT_EVIDENCE`, not failure or bearish signal

## Forbidden actions in this plan

- no ingestion execution
- no DB writes
- no vendor calls
- no live API calls
- no scheduler activation
- no production changes
- no secrets committed
