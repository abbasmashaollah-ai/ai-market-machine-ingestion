# Manual Ingestion Command Verification

`scripts/verify_manual_ingestion_commands.py` is a manual, Railway-safe verification script.

## Scope

The script imports these manual command modules:

- `scripts.inspect_fred_macro_checkpoint`
- `scripts.preview_fred_macro_incremental`
- `scripts.dry_run_fred_macro_incremental`
- `scripts.persist_fred_macro_incremental`

It verifies each module exposes a callable `main()` entrypoint and prints a safe inventory line for each.

## Safety

The script does not:

- require `FRED_API_KEY`
- require `DATABASE_URL`
- call vendors
- write to the database
- schedule work
- run ingestion
- persist checkpoints
- run automatically on Railway startup

This is an operator-run verification only.

`ai-market-machine-data` remains the schema owner.
