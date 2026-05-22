# Manual FRED Macro Run Result Contract

This document defines the in-memory result record for future manual FRED macro incremental runs.

## Scope

The result contract represents the outcome shape of a manual incremental run.

It does not:

- execute the run
- persist state
- call vendors
- write to the database
- schedule work
- create tables
- run migrations

## Fields

- `checkpoint_key`
- `series_id`
- `status`
- `planned_start_date`
- `planned_end_date`
- `rows_planned`
- `rows_fetched`
- `rows_valid`
- `rows_invalid`
- `rows_written`
- `validation_failures`
- `error_message` optional and sanitized
- `started_at`
- `finished_at`

## Status Values

- `planned`
- `running`
- `success`
- `failed`
- `partial`
- `skipped`

## Boundary

`ai-market-machine-data` remains the schema owner.

This repository keeps the result contract in memory only and routes future writes through `app/writers/` if later approved.
