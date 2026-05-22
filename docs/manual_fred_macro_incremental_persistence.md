# Manual FRED Macro Incremental Persistence

`scripts/persist_fred_macro_incremental.py` is a manual command for fetching incremental FRED macro observations, normalizing them, validating them, and optionally writing valid rows through `app/writers/macro_writer.py`.

## Scope

The CLI:

- accepts `--series-id`
- accepts `--category`
- accepts `--all`
- accepts `--start-date`
- accepts `--end-date`
- accepts `--confirm-write`
- requires `FRED_API_KEY`
- requires `DATABASE_URL` only when `--confirm-write` is used
- uses the existing manual incremental selection and dry-run fetch/validate flow
- writes only through `MacroWriter`

## Output

Each series summary prints:

- `series_id`
- `rows_fetched`
- `rows_valid`
- `rows_invalid`
- `rows_written`
- `validation_failures`
- `planned_start_date`
- `planned_end_date`
- `write_confirmed`

## Safety

Without `--confirm-write`, the command performs fetch, normalize, and validate only.

With `--confirm-write`, it writes only valid observations through the approved macro writer.

The command does not:

- create tables
- run migrations
- persist checkpoints
- schedule work
- run automatically on Railway startup

`ai-market-machine-data` remains the schema owner.

