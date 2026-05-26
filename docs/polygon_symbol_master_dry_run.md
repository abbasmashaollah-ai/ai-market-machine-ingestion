# Polygon Symbol Master Dry Run

`scripts/dry_run_polygon_symbol_master.py` is the manual Polygon symbol-master command.

## Behavior

- default mode uses a deterministic sample fixture
- `--live-check` fetches Polygon reference tickers when `POLYGON_API_KEY` is present
- `--confirm-write` requires `DATABASE_URL` and writes through `app.writers.symbol_master_writer.SymbolMasterWriter`
- confirmed writes require `--live-check`; fixture/sample confirmed writes are intentionally blocked
- optional `--record-run`, `--record-quality`, and `--record-lineage` persist approved generic store rows when `DATABASE_URL` is present and the confirmed live path is active
- recording is intentionally not enabled for fixture-only dry runs
- `--limit` defaults to a small safe batch size
- `--max-records` blocks oversized batches before any confirmed write
- `--exchange`, `--asset-type`, `--active-only`, and `--include-inactive` narrow the selected batch
- no scheduler activation
- no FastAPI routes
- no migrations
- no AI/trading/risk/signal/regime/portfolio logic

## Output

- `vendor=polygon`
- `dry_run=true`
- `input_count`
- `normalized_count`
- `valid_count`
- `invalid_count`
- `rows_written`
- `rows_skipped`
- `write_confirmed`
- `limit`
- `max_records`
- `active_filter`
- `exchange_filter`
- `asset_type_filter`

## Boundary

The command does not own schema contracts. Persistence stays bounded to `SymbolMasterWriter` and is only available when `--confirm-write` and `--live-check` are both set.
