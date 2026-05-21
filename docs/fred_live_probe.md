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

- optionally loads a local `.env` file if `python-dotenv` is installed
- reads `FRED_API_KEY` from the environment
- fetches only a recent observation window, defaulting to the last five years
- prints a safe summary with `series_id`, `row_count`, `first_date`, and `last_date`
- never prints the API key
- does not write to the database
- does not write files unless an explicit output flag is provided
- supports `--debug-safe` for zero-row series, printing only response keys and any FRED error message without secrets

## Response Shape

The probe understands the common FRED observation payload shape with rows under the `observations` key. It also accepts a plain list of observation rows for mocked or alternate transport responses.

## Environment Loading

If `python-dotenv` is available in the local environment, the probe attempts to load a local `.env` file before reading `FRED_API_KEY`. This is optional and never committed; `.env.example` remains the template file in the repository.

## Boundary

This probe is not a pipeline, backfill, or scheduler. It is a controlled manual check for API connectivity only.
