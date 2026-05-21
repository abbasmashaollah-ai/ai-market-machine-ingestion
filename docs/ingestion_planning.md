# Ingestion Planning

The ingestion planning layer defines requests, date chunking, checkpoint keys, market-day helpers, and placeholder orchestrator interfaces.

## Scope

This layer provides:

- backfill request and chunk planning
- checkpoint key derivation
- daily update request and schedule configuration
- market-day helpers for weekend exclusion
- placeholder orchestrator and runner interfaces

## Boundary

This layer does not:

- call vendor APIs
- call HTTP services
- write to the database
- implement writers
- execute ingestion pipelines
- execute backfills
- execute schedulers
- expose API routes
- perform AI or trading logic

## Design Notes

- Exchange holidays and early closes are not implemented yet.
- The backfill planner is pure and deterministic.
- Placeholder interfaces define the future execution boundary without providing behavior.
