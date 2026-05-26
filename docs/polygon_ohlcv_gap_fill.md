# Manual Polygon OHLCV Gap Fill

`scripts/fill_polygon_ohlcv_gaps.py` is a manual repair command for filling missing weekday rows in `canonical_ohlcv`.

## Scope

The command:

- accepts `--symbol`
- accepts `--start-date`
- accepts `--end-date`
- accepts `--timeframe`
- accepts `--adjusted` / `--no-adjusted`
- accepts optional `--source-filter`
- accepts `--confirm-write`
- requires `DATABASE_URL` to read coverage state
- requires `POLYGON_API_KEY` only when gaps are present and Polygon fetch is needed
- reads `canonical_ohlcv` first to detect missing weekdays
- writes only through `app/writers/ohlcv_writer.py` when `--confirm-write` is set
- defaults to dry-run/planning mode with `--confirm-write` off
- passes `list[NormalizedOHLCVRecord]` directly into `OhlcvWriter.write()` when writing is enabled
- rejects invalid date ranges before any database or vendor work starts

It does not:

- call FMP
- run automatically on Railway startup
- start a scheduler
- expose API routes
- run migrations
- change schema ownership
- update checkpoints

### Limitation

The gap calculation excludes weekends and a small explicit list of known closures for now. It is not yet a complete exchange calendar.

`ai-market-machine-data` remains the schema owner.

## Output

The command prints:

- `symbol`
- `timeframe`
- `start_date`
- `end_date`
- `source_filter`
- `missing_dates_count`
- `missing_dates`
- `fetched_dates`
- `writable_dates`
- `rows_filtered_out`
- `rows_fetched`
- `rows_valid`
- `rows_written`
- `validation_failures`
- `write_confirmed`
- `status`
- `remaining_missing_dates_count` on confirmed writes
- `adjusted`

## Verification Log

- The command is intended for small manual repair windows before larger backfills.
