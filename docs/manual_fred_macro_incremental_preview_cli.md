# Manual FRED Macro Incremental Preview CLI

`scripts/preview_fred_macro_incremental.py` is a manual read-only CLI for printing the in-memory manual FRED macro incremental preview.

## Scope

The CLI:

- accepts `--series-id`
- accepts `--category`
- accepts `--all`
- accepts `--start-date`
- accepts `--end-date`
- prints the selected series, checkpoint keys, planned date window, and zero-count initial results

## Safety

The CLI does not:

- call vendors
- write to the database
- schedule work
- require `DATABASE_URL`
- require `FRED_API_KEY`
- write files

## Boundary

`ai-market-machine-data` remains the schema owner.
