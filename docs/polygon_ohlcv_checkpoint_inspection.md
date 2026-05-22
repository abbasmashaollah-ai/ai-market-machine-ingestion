# Manual Polygon OHLCV Checkpoint Inspection

`scripts/inspect_polygon_ohlcv_checkpoint.py` is a manual read-only operator tool for inspecting Polygon OHLCV checkpoints.

## Scope

The command:

- accepts repeated `--symbol`
- accepts `--start-date`
- accepts `--end-date`
- accepts `--timeframe`
- prints one checkpoint line per symbol
- prints an aggregate `checkpoint_total` line

It does not:

- call Polygon
- require `POLYGON_API_KEY`
- write to the database
- persist checkpoints
- run automatically on Railway startup

`DATABASE_URL` is required because the command reads checkpoint state from the approved checkpoint contract.

`ai-market-machine-data` remains the schema owner.
