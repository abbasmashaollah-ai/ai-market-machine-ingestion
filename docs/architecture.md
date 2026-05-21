# Architecture Lock

`ai-market-machine-ingestion` is the vendor data ingestion worker for AI Market Machine.

This document is the architecture lock for the repository. It defines the allowed scope, the prohibited scope, and the boundary between ingestion, data governance, and downstream intelligence.

## Target System Architecture

The target architecture is a strict pipeline:

`External Vendors -> ai-market-machine-ingestion -> PostgreSQL/TimescaleDB -> ai-market-machine-data -> ai-market-machine`

The system is split by responsibility:

- ingestion moves and validates data
- data governs and serves data
- AI machine creates intelligence

## Repository Responsibilities

### ai-market-machine-ingestion

This repository is responsible for:

- fetching vendor data
- normalizing vendor payloads
- validating data quality
- reconciling source records
- writing approved records through `app/writers/`
- tracking ingestion jobs, checkpoints, lineage, and quality results

### PostgreSQL/TimescaleDB

The database layer stores operational ingestion state and approved data produced through the ingestion workflow. It is the persistence layer used by the ingestion worker and the data system.

### ai-market-machine-data

This repository owns the canonical data layer. It governs schema, migrations, APIs, and read access for approved data.

### ai-market-machine

This repository owns downstream intelligence. It creates and consumes intelligence, regimes, signals, strategy behavior, and portfolio logic.

## Allowed Responsibilities In Ingestion

Only ingestion-oriented work belongs here:

- vendor adapters and fetchers
- normalization helpers
- validation and quality checks
- reconciliation logic
- checkpoint management
- ingestion run tracking
- lineage capture
- quality result capture
- approved writes through `app/writers/`

## Prohibited Responsibilities In Ingestion

The following are explicitly out of scope:

- AI logic
- trading logic
- FastAPI routes
- schema migrations
- `Base.metadata.create_all()`
- direct database writes outside `app/writers/`
- schema ownership
- regime detection
- signal generation
- strategy logic
- portfolio logic
- risk logic

## Canonical Data Flow

The canonical data flow is:

1. External vendors expose raw data.
2. `ai-market-machine-ingestion` fetches the data.
3. The ingestion layer normalizes, validates, and reconciles the data.
4. Approved records are written through `app/writers/` into PostgreSQL/TimescaleDB.
5. `ai-market-machine-data` governs the canonical schema and serves approved data.
6. `ai-market-machine` consumes governed data to create intelligence.

## Deployment Separation

Deployment responsibilities are separated by repository:

- `ai-market-machine-ingestion` deploys as a worker/data-movement service.
- `ai-market-machine-data` deploys as the canonical data service.
- `ai-market-machine` deploys as the intelligence and application layer.

Do not couple ingestion deployment to downstream application behavior. Do not move schema ownership or read-serving responsibility into the ingestion repository.

## Canonical Reference

The authoritative design reference for this repository is:

`docs/reference/ai_market_machine_ingestion_architecture_framework_v2.pdf`

This document must remain aligned with that PDF and with the strict separation between ingestion, data governance, and AI machine intelligence.
