# Volatility Index Observations Producer Contract

This document defines the producer/backfill contract for populating `volatility_index_observations`.
It is planning and implementation guidance for `ai-market-machine-ingestion` only.
The dry-run producer implementation exists in `app/ingestion/volatility/observations_producer.py`.

## Purpose

Establish the ingestion-side contract for VIX-family observations so the producer can fetch, normalize, validate, backfill, and hand off records to the warehouse writer boundary without owning storage.

## Ownership Boundary

- target owner: `ai-market-machine-data`
- producer owner: `ai-market-machine-ingestion`
- target table: `volatility_index_observations`
- target series: `VIX`, `VVIX`, `VXN`, `RVX`

`ai-market-machine-data` owns the warehouse schema, persistence, and private-read API.
`ai-market-machine-ingestion` owns vendor fetch, normalization, validation, backfill planning, scheduler/runtime orchestration, and writer handoff.
AI Machine reads only later.

## Required Output Field Mapping

The target table must receive the following fields from the producer boundary:

- `symbol`
- `index_family`
- `observation_date`
- `timestamp`
- `value`
- `close`
- `source`
- `source_symbol`
- `source_attribution`
- `daily_or_intraday`
- `lineage`
- `quality_status`
- `certification_status`
- `freshness_status`
- `freshness_checked_at`
- `evidence`

### Field Mapping Summary

- `symbol`: canonical series symbol, one of `VIX`, `VVIX`, `VXN`, `RVX`
- `index_family`: volatility index family classification, expected to remain stable per series
- `observation_date`: canonical business date for the observation
- `timestamp`: upstream observation timestamp when available; otherwise the canonical observation timestamp derived by the producer
- `value`: canonical observation value
- `close`: canonical close-equivalent value for the observation, aligned to the upstream source definition
- `source`: upstream source identifier such as `polygon`
- `source_symbol`: upstream vendor symbol such as `I:VIX`
- `source_attribution`: human-readable source attribution for provenance and downstream display
- `daily_or_intraday`: observation cadence label, expected to reflect the source cadence for the emitted row
- `lineage`: lineage payload describing fetch context, normalization version, request window, and producer provenance
- `quality_status`: quality decision for the row or batch
- `certification_status`: certification decision for the row or batch
- `freshness_status`: freshness decision for the row or batch
- `freshness_checked_at`: timestamp when freshness was evaluated
- `evidence`: evidence payload with enough context to audit the row back to the source payload

## Source Symbol Mapping

Planned vendor mapping for the initial producer path:

- `VIX` -> `I:VIX`
- `VVIX` -> `I:VVIX`
- `VXN` -> `I:VXN`
- `RVX` -> `I:RVX`

The producer should keep canonical symbols stable even if the source symbol format changes later.

## Normalization Rules

- normalize symbols to the canonical set before handoff
- preserve upstream source symbols separately from canonical symbols
- normalize observation dates to an ISO date value
- preserve observation timestamps when present, and derive them deterministically when only date-level data is available
- coerce numeric observation values into a canonical numeric type
- keep `close` aligned with the canonical observation value semantics for the source
- keep `daily_or_intraday` explicit instead of inferring cadence from downstream storage
- do not expand the schema implicitly when a source payload contains extra fields

## Validation Rules

- reject rows missing `symbol`
- reject rows missing `index_family`
- reject rows missing `observation_date`
- reject rows missing `timestamp` when the source requires it for the emitted cadence
- reject rows missing `value`
- reject rows missing `close` when the source semantics require a close-equivalent value
- reject rows missing `source`
- reject rows missing `source_symbol`
- reject rows missing `source_attribution`
- reject rows missing `daily_or_intraday`
- reject rows missing `lineage`
- reject rows missing `quality_status`
- reject rows missing `certification_status`
- reject rows missing `freshness_status`
- reject rows missing `evidence`
- surface validation failures explicitly instead of silently dropping rows

## Quality, Certification, and Freshness Rules

- `quality_status` must be set before handoff
- `certification_status` must be set before handoff
- `freshness_status` must be set before handoff
- `freshness_checked_at` must reflect when freshness was evaluated, not when the source originally published the observation
- certification should stay distinct from quality so a row can be valid yet uncertified
- freshness should stay distinct from both quality and certification so backfill and late-arriving rows remain auditable

## Lineage and Evidence Rules

- preserve source, source symbol, request window, and normalization version in `lineage`
- preserve upstream payload references or hashes in `evidence` when available
- include enough evidence to explain why a row was accepted, rejected, or marked incomplete
- keep lineage and evidence tied to the exact emitted observation, not just to the batch
- do not strip provenance fields before the writer handoff

## Idempotency and Deduplication Expectations

- the producer must emit stable canonical rows for the same observation key
- duplicate observations should collapse to a single warehouse row during writer handoff or warehouse uniqueness enforcement
- the producer should treat repeated backfill runs over the same window as idempotent
- if the upstream source revises a historical observation, the new payload should be traceable through lineage and evidence rather than silently overwriting provenance

## Checkpoint and Backfill Expectations

- backfill must be checkpointed by symbol and observation window
- checkpoints must record the last successfully processed observation boundary
- resumed runs should start after the last successful checkpoint boundary
- checkpoint state must be able to distinguish planned, resumed, completed, and failed backfills
- the producer should support chunked backfill windows so large historical ranges can resume safely

## Source Entitlement Risk

Polygon is the current planned vendor path, but live entitlement for volatility index observations has already shown failure modes in this repo.
That means the producer must assume some live requests may be blocked even when the code path is correct.
The contract therefore requires explicit entitlement failure reporting and does not assume universal live access.

## Explicit Non-Goals For This Step

- no live vendor calls in this step
- no DB writes in this step
- no scheduler activation in this step
- no modification to `ai-market-machine-data`
- no modification to AI Machine
- no secrets exposure

## Current Dry-Run Producer Behavior

- accepts raw dict payloads or normalized volatility records
- maps `I:VIX`, `I:VVIX`, `I:VXN`, and `I:RVX` to canonical symbols
- emits validated payload dictionaries matching the target field contract
- attaches lineage and evidence metadata
- assigns deterministic `quality_status`, `certification_status`, and `freshness_status` values
- returns accepted and rejected payloads without touching the database
- treats source entitlement problems as warnings or explicit rejected records, not crashes
- does not call vendor clients unless the caller injects source records
- does not activate any scheduler path
- a mock writer handoff proof exists in tests and uses the dry-run payloads as writer input
- no real persistence is performed yet
- the next implementation step is an approved writer boundary or a separate live-source dry-run review, depending on readiness

## Future Implementation Sequence

1. Lock the producer record shape and mapping helpers in `ai-market-machine-ingestion`.
2. Add deterministic normalization and validation for the four starter symbols.
3. Add read-only evidence generation for fetch, normalization, and backfill planning.
4. Add checkpointed backfill orchestration with idempotent resume behavior.
5. Add the writer handoff payload that matches the `ai-market-machine-data` table contract.
6. Add contract verification tests before enabling any scheduler or runtime activation.
7. Keep live-source dry-run verification separate from production backfill approval.
8. Only after the warehouse writer boundary is approved, wire persistence in the data repo and then later expose the data to AI Machine.
