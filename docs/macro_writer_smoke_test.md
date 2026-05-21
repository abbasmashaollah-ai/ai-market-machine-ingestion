# Macro Writer Smoke Test

This script is a manual-only database smoke test for the macro writer.

## Script

`scripts/smoke_macro_writer_db.py`

## Purpose

The script verifies that `DATABASE_URL` is present and that the macro writer can perform a tiny controlled write against a real database when the operator explicitly confirms the write.

## Safety Rules

- it does not run automatically on Railway startup
- it defaults to a dry check
- it only writes when `--confirm-write` is passed
- it does not create tables
- it does not run migrations
- it does not delete data
- it does not print `DATABASE_URL`

## Smoke Record

- `series_id`: `INGESTION_SMOKE_TEST`
- `source`: `FRED`
- `observation_date`: `2000-01-01`
- `value`: `1.0`

## Boundary

`ai-market-machine-data` remains the schema owner.
