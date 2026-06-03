# Sector Rotation Dry-Run Vertical Slice Checkpoint

## Purpose

This checkpoint records the completion of the `sector_rotation` dry-run vertical slice in `ai-market-machine-ingestion`.

The slice is complete as an in-memory proof path only. It calculates deterministic sector evidence from sample price histories, builds warehouse-shaped payloads, validates those payloads, and hands them to a mock writer. It does not persist data and it does not activate production orchestration.

## Implemented Layers

The following layers are implemented in the sector rotation package:

- sector universe definitions
- pure return calculations
- relative strength calculations
- deterministic ranking
- leadership and deterioration flags
- momentum score helper
- defensive, rate-sensitive, cyclical, growth, and risk-on group scores
- sector dispersion and breadth-style evidence
- daily summary evidence
- warehouse-shaped observation builders
- deterministic payload validators
- mock writer handoff
- dry-run orchestration over in-memory price histories
- pure row-to-history transformation for certified OHLCV input is now planned/implemented as the next source-shaping step

## Complete Dry-Run Flow

The dry-run path is:

1. accept in-memory price histories keyed by symbol
2. require `SPY` as the benchmark
3. calculate symbol returns
4. calculate relative strength versus `SPY`
5. build the leadership snapshot
6. calculate group scores and dispersion evidence
7. build `sector_rotation_observations`
8. build `sector_rotation_daily_summary`
9. validate both payload families
10. hand off to the mock writer

The target data repo tables for the eventual production contract are:

- `sector_rotation_observations`
- `sector_rotation_daily_summary`

## Safety Boundaries

This checkpoint stays inside the ingestion boundary and does not cross into production persistence.

Explicitly out of scope here:

- no real writer
- no DB writes
- no vendor calls
- no scheduler activation
- no `ai-market-machine-data` changes
- no `AI Machine` changes
- no final market regime logic
- no judge posture
- no buy/sell logic
- no capital allocation
- no portfolio decisions

## What the Dry-Run Proves

The dry-run proves:

- the sector rotation feature package is internally consistent
- the deterministic calculation flow works end to end in memory
- the warehouse-shaped payloads are buildable from the feature outputs
- the validators can reject malformed payloads before handoff
- the mock writer can accept validated payloads without touching storage
- the vertical slice can be exercised without vendors or a scheduler

## What It Does Not Prove

The dry-run does not prove:

- production persistence into `ai-market-machine-data`
- writer contract correctness against the warehouse repo
- DB credentials, permissions, or write-path stability
- source-reader integration against certified OHLCV
- backfill behavior against a real data source
- scheduler timing or daily automation behavior
- downstream AI Machine interpretation or decision quality

## Remaining Steps Before Production

1. real writer contract review
2. data repo write/auth path confirmation
3. source reader integration for certified OHLCV
4. controlled persistence dry-run
5. backfill plan
6. daily job/orchestration
7. scheduler activation last

## Recommended Next Step

Review the writer boundary and the data repo write contract before any real persistence work, then use the certified OHLCV reader plan and the pure row-to-history transformer to shape the source-reader integration.

If a runtime adapter is desired next, review `docs/sector_rotation_certified_ohlcv_adapter_review.md` first; it currently blocks implementation until a data-read client contract exists.

The shared read contract is now documented in `docs/data_read_client_contract.md`.

The mocked `DataReadClient` implementation exists, but sector rotation runtime adapter activation remains blocked until the live read endpoint and response shape are confirmed.

The sector rotation certified OHLCV adapter exists in mocked/test-only form; live endpoint verification is still pending.

The live sector rotation read plan is documented in `docs/sector_rotation_certified_ohlcv_live_read_plan.md`.
