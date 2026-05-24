# Canonical Contract Runtime Enforcement

This document defines the ingestion-side runtime enforcement rule for canonical contracts.

## Rule

`ai-market-machine-data` defines canonical standards. `ai-market-machine-ingestion` enforces them at runtime.

## Ingestion Must Follow

- schemas
- timestamp policy
- lineage standards
- canonical enums
- field names
- quality specifications
- read API contracts

## Ingestion May Own

- vendor fetching
- retries
- checkpoints
- runtime validation
- normalization execution
- approved writes
- backfills
- flat files
- websocket work
- scheduler execution

## Ingestion Must Not Own

- canonical schema definitions
- migrations
- canonical table structure
- indexes
- timestamp policy authority
- lineage contract authority

## Boundary

Runtime validators are allowed only if their expectations trace back to data-owned contracts.

Write orchestration is allowed, but schema ownership is not.

## Safety

This plan is read-only. It does not:

- move files
- delete files
- call vendors
- read or write the database
- change runtime behavior
- change scheduler behavior
- change API behavior
- add schema changes or migrations
- add AI, trading, risk, signal, regime, or portfolio logic

No AI, trading, risk, signal, regime, or portfolio logic belongs in ingestion runtime.
