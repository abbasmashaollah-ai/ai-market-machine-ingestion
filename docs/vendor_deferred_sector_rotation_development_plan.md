# Vendor-Deferred Sector Rotation Development Plan

## Purpose

This plan defines the next sector rotation development path after live coverage showed that the 11 sector ETFs do not yet have certified OHLCV warehouse coverage.

The goal is to keep `sector_rotation` moving with fixtures, mocks, contracts, validators, dry-runs, and existing certified data only, without requiring paid vendor activation now.

## Live Coverage Blocker Summary

The live coverage blocker is documented in `docs/sector_rotation_live_coverage_blocker.md`.

Observed live result:

- `SPY` is populated with certified OHLCV
- `XLC`, `XLY`, `XLP`, `XLE`, `XLF`, `XLV`, `XLI`, `XLB`, `XLRE`, `XLK`, and `XLU` are missing certified OHLCV coverage

## Vendor Subscription Intentionally Deferred

Vendor subscription is intentionally not activated yet.
vendor subscription intentionally deferred

That means:

- no paid vendor activation is required now
- no live vendor backfills should be planned as the next step
- the next step should not depend on paid vendor access

## Why Real Writer and Scheduler Remain Blocked

Real writer/persistence remains blocked because the live warehouse coverage required for production sector rotation is incomplete.
real writer/persistence remains blocked

Scheduler activation remains blocked because the production pipeline cannot safely run without certified OHLCV coverage for the full sector universe.
scheduler activation remains blocked

## Safe Work That Can Continue

- fixture OHLCV histories for `SPY` plus the 11 sector ETFs
- adapter tests with production-shaped payloads
- validator hardening
- dry-run reporting
- writer contract review without persistence
- future backfill plan docs

## Unsafe Work For Now

- live vendor backfills
- production DB writes
- scheduler activation
- AI Machine integration

## Recommended Next Implementation

Create production-shaped sector ETF OHLCV fixtures and fixture-based dry-run tests.

This keeps the feature pipeline moving without depending on paid vendor activation or live warehouse completeness.

## Future Unlock Condition

The next runtime unlock requires all of the following:

1. vendor subscription or an approved alternate historical data source
2. sector ETF OHLCV warehouse coverage
3. live coverage check passes for `SPY` plus the 11 sector ETFs

## Decision Rule

Do not proceed to real writer work until all required sector ETFs have certified OHLCV coverage.

## Explicit Non-Goals

- no runtime code change
- no DB writes
- no vendor calls
- no scheduler activation
- no `AI Machine` changes
- no `ai-market-machine-data` changes
