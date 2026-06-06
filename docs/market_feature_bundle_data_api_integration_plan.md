# Market Feature Bundle Data API Integration Plan

## Status

`READY_FOR_DATA_API_INTEGRATION_PLANNING`

## Purpose

- safely migrate AI Machine data inputs to `ai-market-machine-data` read APIs
- preserve AI Machine judgment and reasoning
- remove only old data/ingestion responsibilities from AI Machine over time
- keep the first implementation read-only and shadow-only

## Current Completed Upstream Bridge

- `ai-market-machine-ingestion` calculates and packages evidence
- `ai-market-machine-data` stores and serves certified evidence
- route: `GET /internal/read/market-feature-bundle/{universe}`
- first universe: `SPY`
- `dataset_version`: `production_pilot.v1`
- `validation_status: PASS`
- `certification_status: CERTIFIED`
- `coverage_status: COMPLETE`
- `quality_status: PASS`

## Preserve As AI Machine Judgment

These areas are `KEEP` and should not be replaced by the data API:

- `app/features/market_risk/**`
- `app/features/market_regime/**`
- `app/features/macro_liquidity/**`
- `app/features/flows_positioning/**`
- `app/features/cross_asset/**`
- `app/features/breadth/**`
- `app/features/liquidity_rates/**`
- `app/features/volatility/**`
- `app/features/news_sentiment/**`
- `app/features/options/**`
- `app/features/earnings/**`
- `app/features/fundamentals/**`
- `app/features/prices/**`
- `app/features/sector_rotation/**` except carefully scoped read boundary work

These modules are AI Machine reasoning, interpretation, judgment, regime, risk, portfolio, signal, confidence, or decision logic. They consume evidence, not judgment, and are not the evidence source.

## Replace-Later Candidates

These are quarantine and replacement candidates, not immediate delete targets:

- `app/vendors/**`
- `app/normalization/**`
- `app/ingestion/**`
- old vendor fetch scripts
- old local data loaders
- old direct persistence/checkpoint workflows where they are only serving AI consumer input
- `app/features/sector_rotation/sector_rotation_reader.py` input-fetching section only
- `app/features/market_features/market_feature_bundle.py` source acquisition only
- `app/features/prices/price_feature_job.py` input-loading section only if applicable

These paths should be treated as legacy input plumbing until the read-only data API path is proven.

## First Integration Approach

- add or formalize a read-only Data API adapter in `app/clients/data_read_client.py`
- no writes
- no vendor calls
- no DB access from AI Machine
- token via env var only
- redacted logs only
- no full idempotency key
- no DB URL

The adapter should only fetch certified evidence and shape it into AI Machine input structures.

## First Candidate Integration Point

`app/features/sector_rotation/sector_rotation_reader.py` is the cleanest adapter boundary identified by the inventory.

- keep sector rotation calculations unchanged
- replace only input-fetch/data-loading portion
- do not change rotation scoring or report logic

This is the safest place to validate the new read path without changing judgment.

## shadow mode

- read bundle from data API
- transform to expected AI input shape
- compare with existing local or legacy input
- log differences
- do not change decisions
- no capital impact
- no portfolio changes
- no user-facing recommendation

Shadow mode is the first acceptable consumer mode because it verifies parity while keeping AI Machine behavior stable.

## Consumption Gates

- route must return `200`
- `certification_status` must be `CERTIFIED`
- `validation_status` must be `PASS`
- `coverage_status` should be `COMPLETE`
- `quality_status` should be `PASS`
- `missing_data_evidence` empty
- `stale_data_evidence` empty or explicitly handled
- unsupported `schema_version` blocks consumption
- missing-data response means no evidence, not negative evidence

If any gate fails, AI Machine must not infer a negative market condition from the absence of evidence.

## Forbidden Changes

- no judge posture changes
- no trading decision changes
- no risk posture changes
- no portfolio allocation changes
- no capital logic changes
- no execution logic
- no scheduler/backfill activation
- no production writes
- no deletion of legacy data files in the first phase

## Staged Migration Plan

1. docs-only plan
2. add adapter tests
3. add read-only client configuration
4. add one shadow-mode consumer
5. compare old vs new input
6. mark old data fetch paths legacy
7. quarantine only after verified parity
8. delete only after repeated verification and explicit approval

The migration should be incremental and reversible until parity is proven.

## Tests Required Before Implementation

- adapter unit tests with mocked route responses
- route failure tests
- uncertified response tests
- missing response tests
- stale response tests
- no vendor call tests
- no DB write/import tests
- boundary tests proving AI reasoning modules are not modified

These tests should prove the adapter boundary without enabling runtime integration.

## Final Recommended Next Action

Create an implementation plan for the read-only Data API adapter.

Do not implement runtime integration until the plan is approved.
