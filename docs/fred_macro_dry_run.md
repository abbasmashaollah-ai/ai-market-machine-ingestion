# FRED Macro Dry Run

`scripts/probe_fred_macro_dry_run.py` is a manual dry-run executor for the future FRED macro ingestion pipeline.

## Purpose

The script fetches FRED macro observations, normalizes them in memory, validates them in memory, and prints safe per-series summaries. It is intended for manual verification only.

## Behavior

- loads `FRED_API_KEY` from the environment, optionally via local `.env` if supported
- defaults to priority 1 active catalog series
- supports `--series-id` to target specific series
- supports `--category` to target a catalog category
- supports `--all` to probe all active catalog series
- prints safe summaries only:
  - `series_id`
  - `rows_fetched`
  - `rows_normalized`
  - `validation_failures`
  - `first_date`
  - `last_date`
- does not write to the database
- does not write files unless `--output` is explicitly provided

## Boundary

This dry-run executor is not a pipeline, backfill, or scheduler. It does not persist any data.
