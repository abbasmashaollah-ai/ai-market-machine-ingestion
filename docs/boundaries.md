# Boundaries

These rules are non-negotiable for `ai-market-machine-ingestion`.

## 1. Separation of concerns

Keep ingestion, canonical data ownership, and downstream intelligence in separate repositories and separate deployment units.

## 2. No intelligence leak

Do not add trading, regime, signal, strategy, portfolio, or risk logic to ingestion. Ingestion moves and validates data; it does not decide what the data means.

## 3. Schema ownership belongs to ai-market-machine-data

Canonical schema, table definitions, and data-serving contracts belong to `ai-market-machine-data`.

## 4. Ingestion may only write to approved tables

Ingestion may write only to tables that are part of the approved ingestion/data contract. It may not invent new canonical tables or write outside the approved boundary.

## 5. No canonical migrations in ingestion

Do not add Alembic migrations or any other canonical schema migration work here.

## 6. No `Base.metadata.create_all()`

Do not create tables from this repository at runtime or during application startup.

## 7. All DB writes must go through `app/writers/`

Database mutation must be routed through writer modules only. Do not add direct ad hoc persistence paths elsewhere in the codebase.

## 8. Backfills must be idempotent

Backfill runs must be safe to rerun without duplicating approved records or corrupting operational state.

## 9. Checkpoints are required for backfills

Backfills must track progress with checkpoints so interrupted work can resume safely.

## 10. Quality validation must happen before canonical writes

Data quality checks must complete before approved records are written.

## 11. Lineage must be recorded

Every meaningful ingestion flow must preserve lineage from source input to approved output.

## 12. Config must come from environment variables

Do not hardcode secrets, endpoints, or deployment-specific values. Use environment-driven configuration only.

## 13. Ingestion must deploy separately from ai-market-machine-data

`ai-market-machine-ingestion` is a worker/data-movement repo. It must not be deployed as the canonical data service.

## 14. No Redis, Kafka, Celery, or complex orchestration until explicitly requested

Do not introduce infrastructure for distributed orchestration unless the requirement is explicitly approved.

## Examples

### Belongs in ingestion

- vendor fetchers
- normalization helpers
- validation and quality checks
- reconciliation routines
- checkpoint handling
- lineage capture
- approved writes through `app/writers/`

### Belongs in ai-market-machine-data

- canonical table schemas
- Alembic migrations
- data-serving APIs
- read models for approved data
- schema evolution and ownership

### Belongs in ai-market-machine

- intelligence generation
- regime detection
- signal logic
- strategy logic
- portfolio logic
- risk logic
- downstream decision-making
