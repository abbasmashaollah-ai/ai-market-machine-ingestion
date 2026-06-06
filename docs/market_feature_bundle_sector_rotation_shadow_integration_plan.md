# Market Feature Bundle Sector Rotation Shadow Integration Plan

## Purpose

- define a safe shadow-mode path for sector rotation input migration
- use the market_feature_bundle Data API adapter as a certified evidence source
- keep sector rotation calculations unchanged
- compare old/local input to new data API input
- do not change AI Machine decisions

This plan is shadow-only and does not authorize runtime wiring yet.

## Current Adapter State

- `app/clients/data_read_client.py` exists
- `tests/unit/test_market_feature_bundle_data_read_client.py` exists
- mocked success/failure/gating tests pass
- no runtime wiring yet
- no live API calls

The adapter is already test-proven as a read-only client boundary.

## First Consumer Boundary

The first consumer boundary remains `app/features/sector_rotation/sector_rotation_reader.py`.

- replace only input-fetch/data-loading section in a later implementation
- do not modify rotation scoring
- do not modify leaderboards
- do not modify report generation
- do not modify market regime
- do not modify market risk
- do not modify macro liquidity
- do not modify flows positioning

The later implementation must leave the deterministic sector rotation logic intact.

## Shadow-Mode Behavior

- fetch legacy/local input as currently done
- fetch market_feature_bundle evidence through `data_read_client` only when an explicit shadow flag is enabled
- transform API evidence into a comparable sector rotation input shape
- compare section availability, dates, symbols, prices/returns if present, and warnings
- log/report differences only
- no behavior change
- no capital impact
- no portfolio changes
- no user-facing recommendation
- no route result becomes authoritative in the first phase

The shadow path is diagnostic only.

## Consumption Gates

- route returns 200
- `certification_status CERTIFIED`
- `validation_status PASS`
- `coverage_status COMPLETE`
- `quality_status PASS`
- supported `schema_version market_feature_bundle.v1`
- `missing_data_evidence` empty
- `stale_data_evidence` empty or explicitly handled
- missing/no-evidence means skip shadow comparison, not negative evidence

If the bundle is missing or not certified, the adapter result should not be used to infer a negative market state.

## Safety Boundaries

- no judge posture changes
- no trading decision changes
- no risk posture changes
- no portfolio allocation changes
- no capital logic changes
- no execution logic
- no scheduler/backfill
- no production writes
- no vendor fetch added
- no DB imports
- no deletion of legacy data files
- no full idempotency_key
- no token/DB URL logging

These boundaries preserve AI Machine reasoning and keep the shadow path non-authoritative.

## Test Plan For Later Implementation

- mocked adapter success response
- mocked no-evidence response
- mocked route failure response
- unsupported schema response
- shadow flag disabled means current behavior unchanged
- shadow flag enabled compares but does not alter output
- source scan proving no `market_risk`/`market_regime`/`macro_liquidity`/`flows_positioning` changes
- source scan proving no DB/vendor/write behavior added
- no live API calls in tests

The tests must prove the shadow path is inert when disabled and diagnostic when enabled.

## Implementation Sequence After Approval

1. inspect `sector_rotation_reader.py` current input boundary
2. add tests around existing behavior first
3. add shadow helper behind explicit flag
4. mock `data_read_client` responses
5. compare legacy vs API evidence
6. keep output identical when shadow mode is disabled
7. produce diagnostic report only when shadow mode is enabled
8. do not make the API path authoritative until separate approval

This sequence keeps the current reader behavior stable until parity is proven.

## Approval Gates

- plan approved
- current `sector_rotation_reader.py` behavior captured by tests
- shadow helper tests pass
- no feature output changes with shadow disabled
- manual local route check separately approved if needed
- authoritative switch requires separate approval

No runtime wiring should occur before these gates are satisfied.
