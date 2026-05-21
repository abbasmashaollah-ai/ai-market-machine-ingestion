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
- it accepts `postgresql://` and `postgres://` URLs on the confirmed write path
- if the Postgres driver is missing, it prints a clear dependency message
- it does not create tables
- it does not run migrations
- it does not delete data
- it does not print `DATABASE_URL`

## Failure Output

When a confirmed smoke write fails, the script prints:

- `status`
- `written`, `skipped`, `failed`
- `error_type`
- `sanitized_error_message`

The sanitized error message must not include `DATABASE_URL`, usernames, passwords, tokens, or other credentials.
Postgres and SQLAlchemy driver connection strings are redacted before printing.

## Smoke Record

- `series_id`: `INGESTION_SMOKE_TEST`
- `source`: `FRED`
- `observation_date`: `2000-01-01`
- `value`: `1.0`

## Boundary

`ai-market-machine-data` remains the schema owner.
