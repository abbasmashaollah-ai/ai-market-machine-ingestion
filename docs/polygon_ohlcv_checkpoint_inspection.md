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

## Verification Log

- Live checkpoint verification completed with:
  - command: `python -m scripts.inspect_polygon_ohlcv_checkpoint --symbol SPY --start-date 2025-01-02 --end-date 2025-01-10 --timeframe 1d`
  - `checkpoint_found=true`
  - `checkpoint_key=polygon:ohlcv:SPY:1d:2025-01-02:2025-01-10`
  - `status=completed`
  - `last_successful_observation_date=2025-01-10`
- The matching persistence run completed successfully after the `canonical_ohlcv` sequence drift was repaired in `ai-market-machine-data`
