# Ingestion Architecture State Review

**Final filename:** `docs/system_review_ingestion_architecture_state.md`

**Status:** REVIEW ONLY / NO IMPLEMENTATION / NO VENDOR CALLS / NO DB WRITES

**Repository:** `ai-market-machine-ingestion`

## Purpose

Provide a deep review of the ingestion repository tree, boundaries, build state, handoff patterns, and future-domain constraints so later work stays aligned with the producer/warehouse/AI split.

## Three-System Architecture

- This review uses the term `three-system architecture` to mean the producer, warehouse, and AI Machine split described below.
- `ai-market-machine-ingestion` is the producer, vendor-processing, normalization, and handoff-builder repo.
- `ai-market-machine-data` is the canonical warehouse and certified read-service repo.
- `ai-market-machine` is the intelligence, regime, risk, portfolio, and decision-support repo.

## Repository Tree Summary

### Top-level structure

- `app/`
- `scripts/`
- `tests/`
- `docs/`
- `outputs/`
- `main.py`
- `pyproject.toml`
- `railway.json`
- `README.md`
- local environment files such as `.env` and `.env.example`

### Major `app/` areas

- `app/vendors/` for live vendor clients, adapters, and transport helpers
- `app/vendor_flat_files/` for vendor flat-file parsing, inspection, and handoff building
- `app/normalization/` for raw-to-canonical shaping
- `app/features/` for deterministic feature calculations and dry-run orchestration
- `app/ingestion/` for vendor ingestion, daily flows, backfills, and manual runners
- `app/writers/` for approved persistence and handoff boundaries
- `app/state/` for lineage, checkpoints, ingestion run state, and quality results
- `app/sources/` for source planning and availability definitions
- `app/market_calendar/` for calendar helpers/providers
- `app/monitoring/` for metrics, alerts, and logging context
- `app/options/` for JSONL options handoff support
- `app/warehouse/` for guarded warehouse-facing ingestion-side persistence services

## Current Domain Inventory

### Clearly active producer domains

- OHLCV
- symbol master
- volatility index
- breadth / participation
- cross-asset OHLCV
- earnings
- event calendar
- fundamentals
- flows / positioning
- liquidity rates
- macro liquidity
- news sentiment
- options
- sector rotation

### Ingestion-capable source/adaptor surface

- Polygon OHLCV
- Polygon symbol master
- Polygon volatility index
- FMP OHLCV
- FRED macro
- vendor flat files for Polygon OHLCV and options
- local fixture-backed market feature bundle flow

### Planning-heavy or partially mature areas

- options producer flow still has planning and boundary docs around vendor acquisition and handoff
- some calendar and market-regime pieces are feature/dry-run oriented rather than live production orchestration
- some domains are more fully modeled in docs/tests than in direct live producer execution

## Current Handoff Contract Inventory

- JSONL options handoff writer/reader in `app/options/options_handoff_jsonl.py`
- options day-aggregates handoff builder/parser/inspector/normalizer/quarantine in `app/vendor_flat_files/options/`
- OHLCV handoff builders and writer contracts in `app/vendor_flat_files/` and `app/writers/`
- market feature bundle producer payload and mock writer in `app/features/market_features/`
- sector rotation writer/report/reader/job dry-run path
- flows / positioning writer and dry-run path
- volatility writer and dry-run path
- canonical writer helpers in `app/writers/`
- lineage writer and state stores in `app/writers/` and `app/state/`

## Current Parser / Normalizer / Validator Inventory

- raw vendor parser modules in `app/vendor_flat_files/`
- normalization modules in `app/normalization/`
- feature-domain validators in `app/features/*_validator.py`
- writer-side contract enforcement in `app/writers/`
- options JSONL validation in `app/options/options_handoff_jsonl.py`
- quarantining support for invalid options flat-file rows

## Current Fixture / Dry-Run Inventory

- market feature bundle fixture dry-runs
- sector rotation dry-runs
- volatility dry-runs
- options dry-runs
- news sentiment dry-runs
- flows / positioning dry-runs
- breadth dry-runs
- cross-asset dry-runs
- event calendar and fundamentals dry-runs
- manual FRED and Polygon runner previews
- JSONL options handoff dry run in ingestion

## Current Docs / Tests Inventory

- architecture and boundary docs
- preflight and readiness docs across vendor, ingestion, and feature slices
- deep architecture review docs
- numerous docs/tests for domain slices, dry runs, fixture validation, and handoff contracts
- content tests for most docs and implementation packages

## Current Build Strengths

- clear producer/warehouse/AI separation
- strong boundary language in docs
- substantial deterministic feature code
- many dry-run and fixture-based tests
- guarded writer abstractions instead of ad hoc DB mutation
- lineage, checkpoint, and quality-result state support
- calendar and preflight helpers that keep future work reviewable
- JSONL handoff shape established for options

## Current Gaps

- not every domain has a fully approved live producer-to-warehouse contract
- some domains are still planning-heavy rather than fully activation-ready
- some live vendor paths remain gated behind entitlement or approval
- ingestion still contains broad feature-area scaffolding that must stay bounded to producer duties
- warehouse-side ownership and API contracts live in the data repo, so ingestion must not drift into schema or read-service ownership

## Architecture Risks

- warehouse ownership drift if ingestion starts to own canonical schema or API behavior
- direct DB write paths outside approved writers
- live vendor calls without explicit boundary or entitlement review
- secrets exposure in docs, logs, tests, or sample artifacts
- duplicated contract logic between ingestion and `ai-market-machine-data`
- AI/trading/risk/regime/portfolio logic leaking into the producer layer
- overbuilding future domains before the data-repo acceptance contract exists

## Boundary Violations Found

- no explicit architecture violations were introduced by this review
- existing risks are mostly boundary-pressure risks rather than active violations
- local `.env` files are present in the repo root and must remain uncommitted

## How This Repo Should Support `ai-market-machine-data`

- fetch and normalize vendor data
- stamp source metadata and hashes
- stamp `source_sha256` on supported handoff artifacts where required
- assign `producer_run_id`
- preserve lineage and warning/rejection evidence
- produce replayable JSONL handoff batches where appropriate
- keep validation and quarantine local to ingestion before warehouse acceptance
- hand off canonical-ready records without owning the warehouse schema or APIs

## How This Repo Should Support the AI Machine Indirectly

- provide governed, normalized upstream records
- preserve source attribution and timestamps
- preserve idempotency keys and replayability
- provide rejection evidence and freshness evidence where appropriate
- keep intelligence and decision-making out of ingestion

## News + Sentiment Readiness

### What ingestion would eventually need to build

- news source adapters or flat-file parsers
- normalization for article, publisher, timestamp, symbol/tag, and relevance fields
- validation and quarantine handling
- source hashing and replayable handoff artifacts
- deterministic local dry runs before any warehouse acceptance

### What should not be built yet

- any AI summarization or trading interpretation
- any portfolio or regime logic
- any warehouse persistence assumptions without a data-repo contract
- any scheduler activation before the contract is approved

### What should wait for the data repo acceptance contract

- canonical accepted/rejected row shapes
- replay semantics
- freshness and certification semantics
- read-service exposure rules

### Recommended local-only first slice after approval

- flat-file or fixture ingestion to normalization
- JSONL handoff construction
- validation and quarantine
- local dry-run reporting

## Recommended Next Ingestion Build Sequence

1. Keep options and sector rotation boundary work reviewable, not expanded blindly.
2. Add or refine local handoff builders before any live production work.
3. Build news/sentiment producer plumbing only after the data-repo contract is explicit.
4. Preserve lineage, source hashing, and rejection evidence for every new producer domain.
5. Keep vendor adapters and parsers isolated from normalization and handoff policy.
6. Delay production scheduler activation until approval, monitoring, and rollback paths are defined.

## Explicit Do-Not-Build-Yet List

- AI/trading/risk/regime/portfolio logic
- warehouse schema ownership
- direct canonical read-service ownership
- production DB migrations from ingestion
- live production writes outside approved writer paths
- scheduler activation without approval
- secrets or credentials in docs, tests, logs, or sample artifacts

## Security / Credential Warning

Credential rotation is still required before production or online use because a DB credential was exposed outside the repo during manual testing. Do not store DB URLs, passwords, tokens, or other secrets in this repository.

## Boundary Confirmations

- docs/tests only
- no runtime behavior changed
- no vendor calls
- no downloads
- no DB writes
- no scheduler activation
- no AI/trading/risk/regime/portfolio logic
- no secrets stored
- credential rotation still required before production/online use
