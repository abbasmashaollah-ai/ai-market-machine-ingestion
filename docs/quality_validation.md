# Quality Validation

The quality layer validates normalized records in memory and returns structured results only.

## Scope

This layer provides:

- validation result types
- severity and status enums
- pass/fail/warn helpers
- batch result summaries
- OHLCV checks
- macro observation checks
- count reconciliation helpers
- report shaping for future data-quality persistence

## Boundary

This layer does not:

- write to the database
- use writer modules
- insert `data_quality_results`
- call vendor APIs
- run ingestion pipelines
- run backfills
- start schedulers
- expose API routes
- perform AI or trading logic

## Design Notes

- Validation is pure and deterministic.
- Results are structured so they can later be persisted by a writer layer, but persistence is out of scope here.
- Duplicate candle detection is handled in-memory for a batch and uses the approved uniqueness key shape.
