# Polygon Symbol Master Dry Run

`scripts/dry_run_polygon_symbol_master.py` is the read-only Polygon symbol-master adapter command.

## Behavior

- default mode uses a deterministic sample fixture
- `--live-check` optionally fetches Polygon reference tickers when `POLYGON_API_KEY` is present
- no DB writes
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

## Boundary

The command is for planning and dry-run validation only. It does not own persistence or schema contracts.
