# Manual OHLCV Coverage Diagnostics

`scripts/diagnose_ohlcv_coverage.py` is a manual read-only operator tool for checking weekday coverage in `canonical_ohlcv`.

## Scope

The command:

- accepts `--symbol`
- accepts `--start-date`
- accepts `--end-date`
- accepts `--timeframe`
- optionally accepts `--source`
- requires `DATABASE_URL`
- reads `canonical_ohlcv` only
- computes expected weekdays between the requested dates
- reports missing weekday coverage and observed source/adjustment distribution

It does not:

- call Polygon
- call FMP
- require `POLYGON_API_KEY`
- write to the database
- persist checkpoints
- run automatically on Railway startup

### Limitation

The coverage calculation excludes weekends and a small explicit list of known closures for now. It is not yet a complete exchange calendar and should not be treated as authoritative for future holidays.

`ai-market-machine-data` remains the schema owner.

## Output

The command prints:

- `symbol`
- `timeframe`
- `start_date`
- `end_date`
- `source_filter`
- `expected_weekdays`
- `observed_dates`
- `missing_weekdays`
- `coverage_ratio`
- `first_timestamp`
- `last_timestamp`
- `sources`
- `adjusted_values`
- `sample_missing_dates`

Sample missing dates are capped so the output stays safe and readable.

## Verification Log

- Live read-only coverage diagnostics completed for:
  - command: `python -m scripts.diagnose_ohlcv_coverage --symbol SPY --start-date 2025-01-02 --end-date 2025-01-10 --timeframe 1d`
  - command: `python -m scripts.diagnose_ohlcv_coverage --symbol SPY --start-date 2025-01-02 --end-date 2025-01-10 --timeframe 1d --source polygon_aggregates`
