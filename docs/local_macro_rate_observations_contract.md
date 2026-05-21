# Local Macro Rate Observations Contract

This document is the local reference for the approved write contract for `macro_rate_observations`.

## Authority

The schema owner remains `ai-market-machine-data`.

This repository does not own the schema, migrations, or canonical table lifecycle. It may only implement ingestion-side writer behavior that respects the approved contract.

## Table

- table: `macro_rate_observations`
- model: `MacroRateObservation`

## Columns

- `id`
- `series_id`
- `observation_date`
- `value`
- `source`
- `release_timestamp`
- `revision_timestamp`
- `created_at`

## Natural Key

`series_id + observation_date + source`

## Required Columns

- `series_id`
- `observation_date`
- `source`
- `created_at`

## Nullable Columns

- `value`
- `release_timestamp`
- `revision_timestamp`

## Database-Managed Column

- `id` is database-managed and must not be supplied by ingestion.

## FRED-Specific Source Rule

- `source` for FRED observations should be `"FRED"`.

## FRED Missing Values

- `value` may be `NULL` for FRED `"."` unavailable observations.

## Boundary Reminder

`ai-market-machine-data` remains the schema owner.
