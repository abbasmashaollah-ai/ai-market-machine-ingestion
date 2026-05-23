# Manual OHLCV Overlap Diagnostics

`scripts/diagnose_ohlcv_overlap.py` is a manual read-only operator tool for inspecting overlapping rows in `canonical_ohlcv`.

## Scope

The command:

- accepts `--symbol`
- accepts `--start-date`
- accepts `--end-date`
- accepts `--timeframe`
- requires `DATABASE_URL`
- reads `canonical_ohlcv` only
- groups rows by `symbol + timestamp + timeframe`
- reports overlap statistics for the selected window

It does not:

- call Polygon
- call FMP
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
- `total_rows`
- `unique_timestamp_count`
- `duplicate_timestamp_groups`
- `sources`
- `adjusted_values`
- `per_source_row_counts`
- `per_adjusted_row_counts`
- `sample_duplicate_groups`

Sample duplicate groups are capped so the output stays safe and readable.

## Verification Log

- Live read-only overlap diagnostic completed for:
  - command: `python -m scripts.diagnose_ohlcv_overlap --symbol SPY --start-date 2025-01-02 --end-date 2025-01-10 --timeframe 1d`
  - expected overlap presence: rows already exist across `FMP` and `polygon_aggregates` with both adjusted and unadjusted variants
