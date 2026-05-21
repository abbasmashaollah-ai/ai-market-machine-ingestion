# FRED Macro Pipeline Plan

The FRED macro pipeline plan defines planning contracts for a future macro ingestion pipeline.

## Scope

This layer provides:

- a pipeline request dataclass
- planned fetch task dataclasses
- pure task planning for selected FRED macro series
- a dry-run executor that fetches, normalizes, and validates in memory only

## Boundary

This layer does not:

- call FRED
- write to the database
- implement writers
- execute ingestion pipelines
- run backfills
- start schedulers
- expose API routes
- perform AI or trading logic

## Design Notes

- The pipeline plan is deterministic and pure.
- Planned tasks are vendor/data labels only and do not imply execution.
- `dry_run` defaults to `True` so future callers must explicitly opt into any non-dry-run behavior when it exists.
- The dry-run executor does not write to the database or call writers.
