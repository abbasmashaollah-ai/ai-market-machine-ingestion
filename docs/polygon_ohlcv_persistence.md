# Manual Polygon OHLCV Persistence

`scripts/persist_polygon_ohlcv_incremental.py` is the manual command for fetching, normalizing, validating, and optionally writing Polygon OHLCV observations.

## Scope

The command:

- accepts repeated `--symbol`
- accepts `--start-date`
- accepts `--end-date`
- accepts `--timeframe`
- accepts `--confirm-write`
- accepts `--use-checkpoint`
- accepts `--update-checkpoint`
- requires `POLYGON_API_KEY`
- requires `DATABASE_URL` only when checkpoint or confirmed-write options are used
- writes only through `app/writers/ohlcv_writer.py`
- uses the shared Polygon HTTP transport for live fetches when `POLYGON_API_KEY` is present
- persists symbol-based canonical OHLCV rows; `symbol_id` is not required

## Output

The command prints per-symbol lines plus an aggregate summary line.

## Safety

The command does not:

- create tables
- run migrations
- persist checkpoints unless explicitly requested and a confirmed write succeeds
- run automatically on Railway startup
- print secrets

`ai-market-machine-data` remains the schema owner.

## Verification Log

- Live Polygon OHLCV persistence verification completed with:
  - command: `python -m scripts.persist_polygon_ohlcv_incremental --symbol SPY --start-date 2025-01-02 --end-date 2025-01-10 --timeframe 1d --confirm-write --use-checkpoint --update-checkpoint`
  - symbol summary: `symbol=SPY`, `requested_start_date=2025-01-02`, `effective_start_date=2025-01-02`, `rows_fetched=6`, `rows_valid=6`, `rows_invalid=0`, `rows_written=6`, `validation_failures=0`, `write_confirmed=true`, `status=completed`
  - aggregate: `series_total=1`, `series_completed=1`, `series_failed=0`, `series_skipped=0`, `total_rows_written=6`
- `canonical_ohlcv` sequence drift was repaired in `ai-market-machine-data` before successful persistence
