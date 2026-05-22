# Macro Writer

This document describes the implemented macro writer for `macro_rate_observations`.

## Scope

The writer persists normalized macro observations to `macro_rate_observations` only.

## Behavior

- accepts a DB-API connection, a connection factory, or a connection-like object
- uses `connection.execute()` when available and falls back to `connection.cursor().execute()` for DB-API connections such as psycopg2
- already-open DB-API connections are used directly and are not re-entered as context managers
- `build_macro_writer(connection)` requires an explicit connection or factory
- maps `NormalizedMacroObservation` into the approved macro rate row shape
- does not supply `id`
- converts missing FRED `"."` values to `NULL`
- defaults `source` to `"FRED"` for FRED records when source is absent
- deduplicates records by `series_id + observation_date + source` within a batch
- uses an `INSERT ... ON CONFLICT ... DO UPDATE` strategy when the backend supports it
- commits once per batch
- rolls back on failure
- on failure, returns safe `WriterResult.message` and `WriterResult.details` fields with `error_type` and sanitized `error_message`

## Boundary

The writer does not create tables, run migrations, call `Base.metadata.create_all()`, or own the schema.

`ai-market-machine-data` remains the schema owner.
