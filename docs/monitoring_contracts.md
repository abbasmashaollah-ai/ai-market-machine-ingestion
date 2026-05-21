# Monitoring Contracts

The monitoring layer defines structured metric, alert, and logging-context contracts.

## Scope

This layer provides:

- metric event dataclasses
- alert event dataclasses
- alert severity enums
- helpers for known ingestion failure categories
- structured logging context dictionaries

## Boundary

This layer does not:

- send alerts to external systems
- integrate with a metrics backend
- write to the database
- implement writers
- call vendor APIs
- run ingestion pipelines
- run backfills
- start schedulers
- expose API routes
- perform AI or trading logic

## Design Notes

- Events are shaped for future transport but remain in-memory contracts for now.
- Logging context is structured and intentionally limited to the ingestion identifiers used across the repo.
