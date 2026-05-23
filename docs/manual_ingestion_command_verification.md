# Manual Ingestion Command Verification

`scripts/verify_manual_ingestion_commands.py` is a manual, Railway-safe verification script.

## Scope

The script imports these manual command modules:

- `scripts.inspect_fred_macro_checkpoint`
- `scripts.preview_fred_macro_incremental`
- `scripts.dry_run_fred_macro_incremental`
- `scripts.persist_fred_macro_incremental`
- `scripts.dry_run_polygon_ohlcv_incremental`
- `scripts.persist_polygon_ohlcv_incremental`
- `scripts.run_polygon_ohlcv_tiny_universe_check`
- `scripts.plan_polygon_ohlcv_backfill`
- `scripts.inspect_polygon_ohlcv_checkpoint`
- `scripts.verify_polygon_ohlcv_rows`
- `scripts.diagnose_ohlcv_overlap`
- `scripts.diagnose_ohlcv_coverage`
- `scripts.fill_polygon_ohlcv_gaps`

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
