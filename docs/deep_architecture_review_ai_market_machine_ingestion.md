# Deep Architecture Review: ai-market-machine-ingestion

## Executive Summary

`ai-market-machine-ingestion` is the producer-side worker for AI Market Machine. Its current shape is consistent with the intended boundary: vendor fetch, normalization, validation, checkpointing, lineage/quality capture, and writer handoff. It is not a warehouse service and it is not an intelligence layer.

The repo is materially stronger on planning and boundary definition than on fully realized production execution for the next warehouse migration. It has working code for vendor transport primitives, normalization helpers, quality/lineage/run-state stores, and guarded writers. It also has substantial planning coverage for Polygon OHLCV, flat files, symbol master, breadth, options, and volatility.

For the specific volatility migration question, the repo is not yet ready to own production backfill/write delivery for `VIX`, `VVIX`, `VXN`, and `RVX` into `ai-market-machine-data`. The repo does have a normalization and dry-run foundation for those symbols, but the evidence points to planning-first support, not a fully proven production writer contract into the warehouse repo.

## Current Role Of This Repo

This repository currently acts as:

- vendor fetch layer
- normalization layer
- validation and quality gate layer
- checkpoint/backfill planning layer
- operational run-state and lineage capture layer
- guarded writer boundary layer
- scheduler/daily-run/backfill orchestration layer in planning and partial implementation

What it should not become:

- schema owner
- warehouse read service
- public API service
- intelligence or trading layer

## Current Vendor / Source Adapters

### Present code-level vendor adapters

- Polygon client foundation in `app/vendors/polygon/client.py`
- Polygon volatility adapter in `app/vendors/polygon_volatility_index.py`
- Polygon symbol-master adapter in `app/vendors/polygon_symbol_master.py`
- FMP client foundation in `app/vendors/fmp/client.py`
- FRED client foundation in `app/vendors/fred/client.py`
- shared vendor HTTP/error/throttling primitives in `app/vendors/common/`

### Present ingestion-side source modules

- volatility source planning in `app/sources/volatility_index_sources.py`
- symbol master source planning in `app/sources/symbol_master_sources.py`
- cross-asset OHLCV source planning in `app/sources/cross_asset_ohlcv_sources.py`
- breadth participation source planning in `app/sources/breadth_participation_sources.py`
- options, news, earnings, event, fundamentals, flows source planning modules

### What is absent or not proven here

- no Finnhub live client in active runtime code
- no production-ready flat-file adapter implementation in runtime code
- no warehouse-side read contract implementation in this repo
- no proven volatility producer that is already committed to `ai-market-machine-data`

## Normalization And Validation Flow

The normalization flow is coherent and layered:

- vendor payloads are converted into normalized models
- normalized records are validated before writing
- quality validators and report helpers exist in `app/quality/`
- normalized models include source, vendor symbol, and time semantics for traceability

Relevant evidence:

- `app/normalization/volatility_index.py` defines `NormalizedVolatilityIndexRecord` and validation rules
- `app/normalization/ohlcv.py` and `app/ingestion/ohlcv/normalization.py` define OHLCV normalization paths
- `app/quality/validators.py` and `app/quality/reports.py` define pass/fail/warn result structure and reporting
- `app/writers/ohlcv_writer.py` enforces schema contract checks before persistence
- `app/writers/symbol_master_writer.py` enforces schema contract checks before persistence

Assessment:

- normalization exists and is disciplined
- validation exists and is explicit
- the quality layer is present, but the repo still relies on contract-aware runtime writers rather than a true warehouse API handoff

## Writer / Handoff Flow Into ai-market-machine-data

The repo has guarded write paths, but the handoff is still internally DB-centric rather than repository-boundary-centric.

### What exists

- `app/writers/ohlcv_writer.py` writes to `canonical_ohlcv` after schema/uniqueness checks
- `app/writers/symbol_master_writer.py` writes to `symbol_master` after schema checks
- `app/writers/macro_writer.py` writes macro observations with contract checks
- `app/state/data_lineage_store.py` and `app/state/data_quality_result_store.py` persist operational evidence
- `app/state/ingestion_run_store.py` persists run history and errors

### What this means

The writer boundary is safer than a direct ad hoc DB write path, but it is not yet the same thing as a warehouse contract owned by `ai-market-machine-data`. The current code assumes approved tables exist and checks them at runtime. That is useful for safety, but it is not a full cross-repo producer/consumer contract.

### Architectural implication

The repo can hand off approved records only when the expected tables and indexes exist. It does not currently prove a repo-native, contract-first handoff into `ai-market-machine-data` as a separately owned service boundary.

## Scheduler / Backfill Status

The repo has backfill and scheduler planning foundations, not a fully proven production scheduler.

### Evidence

- `app/ingestion/backfill/planner.py` defines backfill requests and date chunking
- `app/ingestion/daily/scheduler.py` defines schedule configuration
- `docs/ohlcv_scheduler_design.md` states the scheduler is design-only and disabled by default
- `docs/volatility_index_vertical_slice_plan.md` explicitly keeps volatility in planning mode before vendor/scheduler/persistence work
- `docs/polygon_flatfile_source_planning.md` and related flat-file docs describe a future historical/backfill path, not a live one

### Assessment

- backfill planning exists
- checkpoint planning exists
- scheduler enablement is not mature enough to treat as production-safe for a new volatility migration
- flat-file historical backfill is still future-state planning, not an active runtime path

## What Data Domains Are Already Supported

Supported in code or clearly represented by runtime foundations:

- OHLCV
- symbol master
- macro / FRED macro
- volatility index planning and normalization
- lineage persistence
- quality result persistence
- ingestion run history

Supported in planning or preflight form:

- options
- earnings calendar
- event calendar
- news sentiment
- fundamentals / filings
- flows / positioning
- breadth / participation
- cross-asset OHLCV
- Polygon flat files as a future historical path

## What Data Domains Are Missing

Missing or not yet proven as production-ready in this repo:

- a warehouse-owned read contract implementation
- production flat-file ingestion runtime
- a proven volatility warehouse persistence path
- a fully proven scheduler activation path
- a normalized, approved writer contract for the volatility feed into `ai-market-machine-data`
- any Finnhub runtime adapter in active code

## Historical OHLCV Readiness

Historical OHLCV is the strongest production-shaped slice in this repo.

Evidence:

- FMP single-symbol and multi-symbol orchestration exist in `app/ingestion/ohlcv/orchestrator.py` and `app/ingestion/ohlcv/fanout.py`
- OHLCV normalization exists in `app/ingestion/ohlcv/normalization.py`
- OHLCV writer contract enforcement exists in `app/writers/ohlcv_writer.py`
- manual Polygon OHLCV incremental tooling exists in `app/ingestion/manual/polygon_ohlcv_incremental.py`
- checkpoint store support exists for Polygon OHLCV manual flow
- tests cover OHLCV planning, backfill, runtime, scheduler, evidence, and row validation paths

Assessment:

- ready for controlled producer work
- not a warehouse-owned read API
- better suited to continue as producer-side historical feed preparation than to move into AI Machine

## Symbol Master Readiness

Symbol master is moderately mature.

Evidence:

- symbol master model/validation exists in `app/normalization/symbol_master.py`
- Polygon symbol master source adapter exists in `app/vendors/polygon_symbol_master.py`
- symbol master writer exists in `app/writers/symbol_master_writer.py`
- docs define the data-side contract and boundary with `ai-market-machine-data`
- tests cover symbol master planning, population assessment, contracts, and writer behavior

Assessment:

- producer-side source and normalization are in place
- the contract still depends on the data-side schema owner
- safe enough for controlled producer refresh work, but not enough to collapse the boundary into AI Machine

## Volatility VIX/VVIX/VXN/RVX Readiness

This is the key question.

### What exists

- `app/normalization/volatility_index.py` defines the canonical volatility record and validation rules
- `app/vendors/polygon_volatility_index.py` maps `VIX`, `VVIX`, `VXN`, and `RVX` to Polygon vendor symbols and can normalize returned payloads
- `app/ingestion/volatility/polygon.py` defines a dry-run plan and canonical OHLCV-shaped mapping for volatility payloads
- `docs/volatility_index_foundation.md` and `docs/volatility_index_vertical_slice_plan.md` explicitly define the starter symbols and the producer boundary
- `docs/volatility_index_live_dry_run.md` documents a live-check path and notes that `I:VIX` and `I:VXN` returned `401` on the current key
- `docs/volatility_index_live_check_blocked.md` records the blocked state for Polygon live checks

### What is not proven

- no verified production writer path for volatility records into `ai-market-machine-data`
- no proven warehouse contract for the volatility feed
- no evidence that live Polygon entitlement is sufficient for all required volatility observations
- no evidence that the repo already owns the producer/backfill for these symbols in production

### Answer

No, the repo is not ready to produce/backfill `VIX`, `VVIX`, `VXN`, and `RVX` as a production-ready feed into the warehouse direction yet. It has the mapping and normalization scaffolding, but the live source entitlement, warehouse contract, and producer/backfill ownership are not proven enough.

## Quality / Lineage / Checkpoint Coverage

### Present coverage

- lineage store: `app/state/data_lineage_store.py`
- quality result store: `app/state/data_quality_result_store.py`
- ingestion run history: `app/state/ingestion_run_store.py`
- checkpoint abstraction: `app/state/checkpoints.py`
- manual checkpoint stores for Polygon OHLCV and FRED macro
- validation and result summarization utilities

### Assessment

- lineage coverage exists and is structurally sound
- quality evidence coverage exists and is structurally sound
- checkpoint coverage exists, but production integration is not uniform across all domains
- the repo still leans heavily on planning docs and manual/verification tooling for some slices

## Deployment / Runtime Readiness

### Good

- config is env-driven via `app/core/config.py`
- runtime context and logging carry ingestion metadata
- no public API surface is visible in active runtime code
- no schema migrations are present in active runtime code
- db writes are kept behind writer/store layers

### Not yet ready

- no evidence of a full production-ready scheduler activation path for the target domains
- no runtime proof of safe volatility production/backfill at warehouse scale
- no evidence of a complete flat-file producer path

## Operational Risks

1. Contract drift between this repo and `ai-market-machine-data` if writer assumptions diverge from warehouse schema.
2. Overreliance on planning docs for slices that look mature but still lack live entitlement or persistence proof.
3. Volatility source entitlement risk for Polygon, especially given the documented `401` observations.
4. Flat-file historical path may become fragmented if it is built before the official layout and manifest/quarantine policies are settled.
5. Scheduler enablement risk if automation is turned on before calendar, quota, monitoring, and recovery controls are complete.
6. Producer-side evidence may look complete while the actual warehouse contract remains unproven.

## Dependency On ai-market-machine-data Contracts

This repo depends on `ai-market-machine-data` for:

- canonical schema ownership
- migrations
- read contracts
- warehouse service boundaries
- private-read API behavior

Critical point:

- ingestion can validate and prepare records
- ingestion should not define the warehouse contract
- writer success here does not mean the warehouse-side contract is complete unless the data repo has actually stored and served the expected shape

## What Should Be Built Next

1. A confirmed volatility producer contract that matches the warehouse table/read model owned by `ai-market-machine-data`.
2. A clear producer-to-warehouse handoff for `VIX`, `VVIX`, `VXN`, and `RVX`.
3. Proven live-source coverage or an approved source alternative for blocked Polygon observations.
4. A formal checkpointed backfill path for volatility that preserves lineage and quality evidence.
5. A production-grade contract verification command for volatility before any AI Machine migration.
6. If flat files are to be used for historical OHLCV, add discovery, manifest, integrity, quarantine, download, parse, and persistence in that order.
7. Keep symbol master producer refreshes separate from warehouse ownership.
8. Keep FMP OHLCV and Polygon OHLCV producer responsibilities in this repo.
9. Tighten warehouse contract verification around every writer path that crosses repo boundaries.
10. Preserve the strict no-API/no-schema-ownership rule in ingestion.

## What Should Not Be Built Yet

- AI/trading/regime/strategy/portfolio logic
- a public API in this repo
- schema ownership or migrations in this repo
- direct warehouse read-serving endpoints in this repo
- scheduler enablement for volatility before the warehouse contract is confirmed
- flat-file persistence before layout/discovery/manifest/integrity/quarantine are settled
- moving all vendor calls out of ingestion before the ingestion-side producer responsibilities are fully transferred

## Recommended 10-Step Roadmap

1. Confirm the volatility warehouse table and read contract in `ai-market-machine-data`.
2. Define the exact producer payload for `VIX`, `VVIX`, `VXN`, and `RVX`.
3. Verify live source entitlement or approve an alternate source for blocked Polygon index observations.
4. Add a dry-run producer verification command that proves the normalization and validation output without writing.
5. Add a checkpointed volatility backfill plan that can resume safely.
6. Wire the producer handoff to the warehouse contract only after schema ownership is confirmed.
7. Keep lineage and quality persistence mandatory for every accepted volatility batch.
8. If historical OHLCV moves to flat files, implement discovery and download dry-runs first, then parse, then persistence.
9. Delay scheduler activation until calendar, quota, monitoring, and retry/recovery readiness are complete.
10. Leave AI Machine with only read-only consumer/intelligence responsibilities.

## Specific Questions Answered

### Is ingestion ready to produce/backfill VIX, VVIX, VXN, RVX?

No. The repo has normalization and mapping support, but the production-ready source entitlement, warehouse contract, and producer/backfill proof are not complete.

### Does ingestion already have a safe writer path into ai-market-machine-data?

Partially. It has guarded writer/store code and contract checks, but not a proven repo-to-repo warehouse handoff contract. It is safe as an internal DB-writer boundary, not yet proven as a complete cross-repo warehouse producer contract.

### Does ingestion support Polygon flat files or only API paths?

Only API paths are present in runtime code. Polygon flat files are documented as a future historical/backfill path, but the implementation is planning-only in this repo.

### What must be built before `volatility_feed.py` can migrate in AI Machine?

- a confirmed warehouse-side volatility contract
- a stable producer payload and naming contract
- checkpointed backfill behavior
- lineage and quality evidence flow
- proven live-source entitlement or alternate source approval
- a safe warehouse handoff path owned by ingestion, not by AI Machine

### What vendor calls should remain here and not in AI Machine?

Keep vendor fetch and normalization in ingestion:

- Polygon OHLCV fetches
- Polygon symbol-master lookups
- Polygon volatility observation fetches
- FMP OHLCV fetches
- FRED macro fetches
- any other approved vendor fetches needed for ingestion producer duties

AI Machine should not call vendors directly for producer ingestion behavior.

## Final Readiness Rating

**Rating: 71 / 100**

### Why

- Strong boundary discipline and good producer-side decomposition.
- Good coverage of normalization, validation, lineage, checkpointing, and writer guards.
- OHLCV and symbol-master producer work are sufficiently mature to continue.
- Volatility is not yet production-ready for the warehouse/private-read direction because the live source entitlement and cross-repo warehouse contract are not proven.
- Flat-file historical support is still future-state planning.

The repo is solid as a producer workspace. It is not yet complete enough to be treated as the final volatility producer for the new warehouse/private-read architecture.
