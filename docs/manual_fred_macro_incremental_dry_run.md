# Manual FRED Macro Incremental Dry Run

`scripts/dry_run_fred_macro_incremental.py` is a manual dry-run CLI for incremental FRED macro updates.

## Scope

The CLI:

- accepts `--series-id`
- accepts `--category`
- accepts `--all`
- accepts `--start-date`
- accepts `--end-date`
- requires `FRED_API_KEY` for live fetches
- prints safe per-series summaries

## Safety

The CLI does not:

- write to the database
- persist checkpoints
- require `DATABASE_URL`
- schedule work
- write files
- run automatically on Railway startup
- call FRED without an operator-provided API key

## Boundary

`ai-market-machine-data` remains the schema owner.
