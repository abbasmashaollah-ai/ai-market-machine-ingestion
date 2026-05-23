# Manual Polygon OHLCV Row Verification

`scripts/verify_polygon_ohlcv_rows.py` is a manual read-only operator tool for verifying rows already present in `canonical_ohlcv`.

## Scope

The command:

- accepts `--symbol`
- accepts `--start-date`
- accepts `--end-date`
- accepts `--timeframe`
- requires `DATABASE_URL`
- reads `canonical_ohlcv` only
- prints a safe verification summary

It does not:

- call Polygon
- require `POLYGON_API_KEY`
- write to the database
- persist checkpoints
- run automatically on Railway startup

`ai-market-machine-data` remains the schema owner.

## Output

The command prints:

- `symbol`
- `timeframe`
- `start_date`
- `end_date`
- `row_count`
- `first_timestamp`
- `last_timestamp`
- `adjusted_values`
- `sources`

## Verification Log

- Live read-only verification completed with:
  - command: `python -m scripts.verify_polygon_ohlcv_rows --symbol SPY --start-date 2025-01-02 --end-date 2025-01-10 --timeframe 1d`
  - expected row count: `row_count=6`
  - expected timestamps: first and last timestamps within the inserted SPY date range
  - no vendor call
