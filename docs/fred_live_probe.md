# FRED Live Probe

`scripts/probe_fred_series.py` is a manual connectivity probe for FRED.

## Purpose

The probe verifies that the FRED client can reach the API with a tiny controlled request set. It is intended for manual use only.

## Default Series

The probe checks these series by default:

- `GDP`
- `CPIAUCSL`
- `UNRATE`

## Behavior

- reads `FRED_API_KEY` from the environment
- fetches only small recent observation windows
- prints a safe summary with `series_id`, `row_count`, `first_date`, and `last_date`
- never prints the API key
- does not write to the database
- does not write files unless an explicit output flag is provided

## Boundary

This probe is not a pipeline, backfill, or scheduler. It is a controlled manual check for API connectivity only.
