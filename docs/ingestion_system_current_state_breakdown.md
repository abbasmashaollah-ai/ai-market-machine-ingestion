# Ingestion System Current State Breakdown

## A. Purpose

This document is a current-state breakdown of `ai-market-machine-ingestion` before adding a new `app/features/` layer.

The goal is to map what already exists, what each folder is responsible for, what should stay separated, and what the first deterministic evidence vertical slice should be.

## B. Three-System Boundary

The system boundary is strict:

- `ai-market-machine-ingestion` calculates deterministic evidence
- `ai-market-machine-data` stores and serves certified evidence
- `AI Machine` interprets evidence and makes decisions

The boundary statements above are intended to be read literally: ingestion calculates deterministic evidence, data stores and serves certified evidence, and AI Machine interprets evidence.

In plain terms:

- no vendor calls inside feature logic
- no DB writes inside feature logic
- no scheduler activation inside feature logic
- no AI decision logic inside ingestion

Ingestion owns:

- vendor fetching
- normalization
- validation
- checkpointing
- lineage
- quality checks
- deterministic feature calculation
- writer handoff

Data owns:

- schemas
- migrations
- warehouse tables
- certified read APIs
- quality/certification storage

AI Machine owns:

- regimes
- judge
- probability
- confidence
- risk
- portfolio
- decision logic

`AI Machine` interprets the evidence and makes the decision layer choices downstream.

Ingestion must not contain final market regime, judge posture, buy/sell logic, capital logic, or portfolio decisions.

## C. Current Repo Structure Found

The current repository already has the following top-level areas:

- `app/` for runtime code
- `docs/` for architecture, contracts, runbooks, and planning notes
- `tests/` for unit, docs, integration, and e2e checks
- `scripts/` for manual runners, diagnostics, and operator helpers

Within `app/`, the visible responsibilities are:

- `app/vendors/` for vendor clients and vendor-specific adapters
- `app/normalization/` for raw-to-canonical shaping
- `app/sources/` for source planning and source availability decisions
- `app/writers/` for approved persistence handoff
- `app/quality/` for validation and quality support
- `app/state/` for checkpoints, run state, lineage, and quality result storage
- `app/ingestion/` for orchestration flows, daily jobs, manual flows, and backfill coordination
- `app/symbol_master/` for symbol master service logic
- `app/core/` for configuration, exceptions, db/runtime helpers, logging, and health
- `app/monitoring/` for alerting and metrics helpers
- `app/models/` for vendor, normalized, and internal model types
- `app/market_calendar/` for market calendar helpers

## D. Existing Strengths

### Vendor/source foundations

The repo already has vendor client and adapter foundations for Polygon, FRED, FMP, and related shared HTTP/throttling utilities in `app/vendors/`.

### Normalization

The repo already has domain normalization modules in `app/normalization/` for OHLCV, symbol master, macro, volatility, breadth, cross-asset, options, event calendar, and related surfaces.

### Writer/handoff paths

The repo already has guarded writer modules in `app/writers/` and writer-specific contract checks before approved persistence.

### Quality/validation

The repo already has validation and reporting helpers in `app/quality/`, including domain-specific validation logic.

### State/checkpointing

The repo already has `app/state/` for ingestion runs, checkpoints, lineage, quality results, and manual checkpoint helpers.

### Docs/tests discipline

The repo already uses docs-as-contracts and tests that verify documentation language, boundaries, and readiness claims.

### Existing volatility work

There is already a volatility foundation in the repo:

- `app/normalization/volatility_index.py`
- `app/ingestion/volatility/`
- `app/vendors/polygon_volatility_index.py`
- `docs/volatility_index_*`

### Existing dry-run and writer-handoff patterns

The repo already demonstrates dry-run planning and writer-handoff patterns in OHLCV, symbol master, macro, and volatility slices.

## E. Current Gaps

The current gaps are structural, not just domain-specific:

- missing dedicated `app/features/` layer
- missing full feature/evidence vertical slices
- missing breadth producer
- missing sector rotation producer
- missing daily feature orchestration for evidence domains
- missing production writer activation for feature tables if those tables are intended to be persisted

The repo currently has feature-adjacent planning and normalization code scattered across `app/sources/`, `app/normalization/`, and `app/ingestion/`. That is acceptable for planning and payload shaping, but not for deterministic evidence computation.

## F. Recommended Organized Folder Structure

Recommended target structure:

```text
app/features/
  __init__.py
  prices/
  universe/
  breadth/
  sector_rotation/
  volatility/
  options/
  macro_liquidity/
  flows_positioning/
  fundamentals/
  earnings/
  news_sentiment/
  event_calendar/
  cross_asset/
```

Standard pattern inside each domain folder:

- `reader`
- `engine/calculator`
- `observation_builder`
- `validator`
- `writer`
- `job`
- `README.md`

This pattern keeps deterministic evidence logic isolated from source planning and raw payload normalization.

Current status:

- `app/features/` skeleton now exists
- sector rotation package contract docs now exist
- sector universe and relative strength calculation code now exist
- sector leadership ranking and momentum helpers now exist
- defensive/cyclical/risk-on grouping helpers now exist
- sector dispersion and daily summary helpers now exist
- warehouse-shaped observation builders now exist
- deterministic payload validators now exist
- mock writer handoff now exists
- dry-run orchestration job now exists
- sector rotation dry-run vertical slice checkpoint is complete
- next planning step is the certified OHLCV reader contract for sector rotation
- runtime feature engines are not implemented yet
- real persistence/writer behavior is not implemented yet

## G. What Belongs Where

- `app/vendors/` = vendor clients, HTTP adapters, vendor mappers, and transport helpers
- `app/sources/` = source planning, availability, candidate source comparison, and readiness scoring
- `app/normalization/` = raw-to-canonical shaping and payload standardization
- `app/features/` = deterministic evidence calculations and feature observations
- `app/writers/` = approved persistence and writer handoff
- `app/quality/` = validation, certification support, and quality reporting
- `app/state/` = checkpoints, run state, lineage, and run/quality persistence helpers
- `scripts/` = manual runners, inspections, dry runs, and operator tools only
- `docs/` = architecture, contracts, runbooks, and planning docs
- `tests/` = unit, contract, docs, integration, and e2e tests

## H. What Must Not Go Into Ingestion

These responsibilities do not belong in `ai-market-machine-ingestion`:

- final trading decisions
- buy/sell logic
- judge posture
- final market regime decision
- capital allocation
- portfolio decisions
- AI confidence logic

If a calculation is only useful because it feeds an AI decision layer, it still belongs in the downstream system, not here.

## I. First Vertical Slice Recommendation

Two candidate first slices are reasonable:

### Breadth first

Pros:

- aligns with existing breadth/participation planning
- reuses ETF/index universe work
- can be framed as market participation evidence

Cons:

- breadth calculation surface is broader and easier to mix with source planning
- likely requires more upstream universe completeness than sector rotation

### Sector rotation first

Pros:

- narrow, deterministic, and concrete
- uses a fixed ETF universe
- maps directly to existing `sector_rotation_observations` and `sector_rotation_daily_summary`
- easier to keep separate from AI Machine decisions

Cons:

- still requires clean OHLCV access and stable daily orchestration
- should not become a stealth regime engine

### Final recommendation

If the repo already has clean OHLCV access and data repo sector v2 is ready, sector rotation can be first.

If universe membership is already stronger than sector support, breadth can be first.

Otherwise recommend sector rotation first because it uses 11 fixed ETFs plus SPY and maps directly to existing `sector_rotation_observations` and `sector_rotation_daily_summary`.

## J. Proposed Sector Rotation Feature Package

Target files:

```text
app/features/sector_rotation/
  __init__.py
  README.md
  sector_universe.py
  sector_rotation_reader.py
  relative_strength_engine.py
  sector_leadership_engine.py
  defensive_rotation_engine.py
  cyclical_rotation_engine.py
  sector_dispersion_engine.py
  rotation_acceleration_engine.py
  rotation_persistence_engine.py
  sector_rotation_summary_engine.py
  sector_rotation_observation_builder.py
  sector_rotation_validator.py
  sector_rotation_writer.py
  sector_rotation_job.py
```

The package should keep source access, calculation, validation, and persistence handoff separate.

## K. Sector ETF Universe

The sector rotation universe should be:

- `SPY` benchmark
- `XLC`
- `XLY`
- `XLP`
- `XLE`
- `XLF`
- `XLV`
- `XLI`
- `XLB`
- `XLRE`
- `XLK`
- `XLU`

## L. Sector Feature Outputs

The target outputs should include:

### `sector_rotation_observations`

Key fields:

- `return_1d`
- `return_5d`
- `return_20d`
- `return_60d`
- `relative_strength_5d_vs_spy`
- `relative_strength_20d_vs_spy`
- `relative_strength_60d_vs_spy`
- `rank_5d`
- `rank_20d`
- `rank_60d`
- `rank_change_5d`
- `rank_change_20d`
- `momentum_score`
- `leadership_flag`
- `deterioration_flag`

### `sector_rotation_daily_summary`

Key fields:

- `risk_on_leadership_score`
- `defensive_leadership_score`
- `leadership_concentration_score`
- `sector_dispersion_score`
- `broad_rotation_flag`
- `narrow_rotation_flag`
- `improving_rotation_flag`
- `deteriorating_rotation_flag`

The outputs must remain deterministic evidence, not decision outputs.

## M. Recommended Implementation Sequence

1. docs/contracts for `app/features` architecture
2. `app/features/` skeleton only
3. pure sector universe plus return/relative strength engines
4. leadership and defensive/cyclical engines
5. daily summary engine
6. observation builders
7. validators
8. mock writer handoff
9. real writer/persistence only after approval
10. job/orchestration only after dry-run proof
11. scheduler activation last

## N. Risks

- mixing source planning with feature calculation
- writing before validation
- building AI decisions inside ingestion
- starting scheduler too early
- relying on live vendor calls before dry-run tests
- schema drift with `ai-market-machine-data`
- unclear `dataset_version` rules

## O. Next Codex Command Recommendation

Next implementation step: create the `app/features/` skeleton and the `app/features/sector_rotation/` package contract docs only, without any runtime calculation code or persistence code.
