# FRED Macro Series Catalog

The FRED macro series catalog is a documented, config-only inventory of core series we plan to ingest later.

## Scope

This catalog provides:

- a series definition dataclass
- category labels for macro series groups
- the initial core series inventory
- helpers to list active series
- helpers to filter by category
- helpers to look up a series by `series_id`

## Boundary

This catalog does not:

- call FRED
- write to the database
- run backfills
- execute ingestion pipelines
- start schedulers
- expose API routes
- perform AI or trading logic

## Design Notes

- The catalog is configuration only.
- Priority values are small integers where lower means more important.
- Category labels are stable internal labels used for planning and later ingestion work.
