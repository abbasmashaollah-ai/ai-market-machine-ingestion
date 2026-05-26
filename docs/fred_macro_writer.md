# FRED Macro Writer

`FredMacroWriter` is the manual batch persistence path for normalized FRED macro observations.

Boundary:
- writes only through the approved `macro_rate_observations` table shape
- commits once per batch
- rolls back on failure
- does not create tables
- does not run migrations
- does not call vendors

Persistence behavior:
- deduplicates by `series_id + observation_date + source`
- performs idempotent conflict handling against the approved uniqueness key
- persists the approved observation fields only
- leaves vintage and realtime fields deferred
- returns `SKIPPED` when rows are already present
- returns `NO_EFFECT` if the confirmed-write path is invoked but no write result is produced

The writer is only available to the confirmed-write manual path.
