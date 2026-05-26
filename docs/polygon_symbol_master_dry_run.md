# Polygon Symbol Master Dry Run

`scripts/dry_run_polygon_symbol_master.py` is the manual Polygon symbol-master command.

## Behavior

- default mode uses a deterministic sample fixture
- `--live-check` fetches Polygon reference tickers when `POLYGON_API_KEY` is present
- `--confirm-write` requires `DATABASE_URL` and writes through `app.writers.symbol_master_writer.SymbolMasterWriter`
- confirmed writes require `--live-check`; fixture/sample confirmed writes are intentionally blocked
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

## Boundary

The command does not own schema contracts. Persistence stays bounded to `SymbolMasterWriter` and is only available when `--confirm-write` and `--live-check` are both set.
