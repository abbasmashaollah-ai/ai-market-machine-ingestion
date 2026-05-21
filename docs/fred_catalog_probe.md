# FRED Catalog Probe

`scripts/probe_fred_catalog.py` is a manual, safe probe for the active FRED macro series catalog.

## Purpose

The probe checks a small set of cataloged FRED macro series using the existing FRED transport and probe helpers. It is intended for manual verification only.

## Default Behavior

- loads `FRED_API_KEY` from the environment, optionally via local `.env` if supported
- probes only priority 1 active series by default
- supports `--all` to probe all active series
- supports `--category` to probe one category
- uses a small recent observation window by default
- prints a safe summary with:
  - `series_id`
  - `category`
  - `row_count`
  - `first_date`
  - `last_date`
  - `status_code`
- never prints the API key
- does not write to the database
- does not write files unless `--output` is explicitly provided

## Debug Safe Mode

When `--debug-safe` is provided and a series returns zero rows, the probe prints only non-sensitive request and response diagnostics:

- `series_id`
- `status_code`
- `raw_text_length`
- `response_keys`
- `observations_count`
- `fred_error` when present
- request params with `api_key` removed

## Boundary

This probe is not a pipeline, backfill, or scheduler. It does not mutate state or write canonical data.
