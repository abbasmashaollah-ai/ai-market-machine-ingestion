# Manual Polygon OHLCV Gap Fill

`scripts/fill_polygon_ohlcv_gaps.py` is a manual repair command for filling missing weekday rows in `canonical_ohlcv`.

## Scope

The command:

- accepts `--symbol`
- accepts `--start-date`
- accepts `--end-date`
- accepts `--timeframe`
- accepts optional `--source-filter`
- accepts `--confirm-write`
- requires `DATABASE_URL` to read coverage state
- requires `POLYGON_API_KEY` only when gaps are present and Polygon fetch is needed
- reads `canonical_ohlcv` first to detect missing weekdays
- writes only through `app/writers/ohlcv_writer.py` when `--confirm-write` is set

It does not:

- call FMP
- run automatically on Railway startup
- start a scheduler
- expose API routes
- run migrations
- change schema ownership
- update checkpoints

### Limitation

The gap calculation excludes weekends only. Exchange holidays are not handled yet.

`ai-market-machine-data` remains the schema owner.

## Output

The command prints:

- `symbol`
- `timeframe`
- `start_date`
- `end_date`
- `source_filter`
- `missing_dates_count`
- `rows_fetched`
- `rows_valid`
- `rows_written`
- `validation_failures`
- `write_confirmed`
- `status`

## Verification Log

- The command is intended for small manual repair windows before larger backfills.
