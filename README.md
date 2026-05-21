# ai-market-machine-ingestion

`ai-market-machine-ingestion` is the vendor ingestion worker for AI Market Machine.

This repository exists to move vendor data into the system safely and consistently. It fetches external vendor data, normalizes it, validates it, reconciles it, writes approved records, and tracks lineage, checkpoints, and ingestion job state.

## What this repo does

- fetches vendor data from external sources
- normalizes vendor payloads into ingestion-ready shapes
- validates data quality
- reconciles source records against expected canonical-ready data
- writes approved records through `app/writers/`
- tracks ingestion jobs, checkpoints, lineage, and quality results

## What this repo must never do

- no AI logic
- no trading logic
- no FastAPI routes
- no schema migrations
- no `Base.metadata.create_all()`
- no direct database writes outside `app/writers/`
- no schema ownership
- no strategy, regime, signal, portfolio, or risk logic

## System Flow

`External Vendors -> ai-market-machine-ingestion -> PostgreSQL/TimescaleDB -> ai-market-machine-data -> ai-market-machine`

The boundary is strict:

- `ai-market-machine-ingestion` handles vendor fetch, normalization, validation, reconciliation, approved writes, lineage, and checkpoints.
- `ai-market-machine-data` owns schema, migrations, APIs, and read access.
- `ai-market-machine` owns intelligence, regimes, signals, strategy, and portfolio logic.

## Canonical Reference

The architecture for this repository is defined by the canonical PDF:

`docs/reference/ai_market_machine_ingestion_architecture_framework_v2.pdf`

That document is the source of truth for the ingestion boundary and repository responsibilities.
