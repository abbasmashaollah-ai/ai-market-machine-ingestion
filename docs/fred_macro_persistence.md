# FRED Macro Persistence

`scripts/persist_fred_macro.py` is a manual command for fetching FRED macro catalog data, normalizing it, validating it, and optionally writing valid observations into `macro_rate_observations`.

## Scope

This command:

- loads `FRED_API_KEY` and `DATABASE_URL` from the environment, optionally via local `.env`
- defaults to priority 1 active FRED catalog series
- supports `--series-id`
- supports `--category`
- supports `--all`
- supports `--confirm-write`
- prints per-series `rows_fetched`, `rows_valid`, `rows_written`, and `validation_failures`
- uses the existing FRED client, normalization, validation, and macro writer

## Write Behavior

- without `--confirm-write`, the command prints a planned write summary only
- with `--confirm-write`, it writes valid rows into `macro_rate_observations`
- invalid rows are skipped safely
- secrets are never printed

## Boundary

This command is manual-only and does not run automatically on Railway startup.

`ai-market-machine-data` remains the schema owner.
