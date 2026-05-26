# Polygon Symbol Master Targeted Lookup

`scripts/fetch_polygon_symbol_master_by_symbols.py` is the manual targeted lookup command for explicit ETF/index candidate symbols.

## Behavior

- accepts repeated `--symbol`
- optionally accepts `--from-etf-index-candidates`
- default mode is dry-run
- `--live-check` requires `POLYGON_API_KEY`
- `--confirm-write` requires `DATABASE_URL` and `--live-check`
- writes only through `app.writers.symbol_master_writer.SymbolMasterWriter`
- prints `requested_count`, `found_count`, `missing_count`, `valid_count`, `invalid_count`, and `rows_written`

## Boundary

- no scheduler
- no FastAPI routes
- no migrations
- no schema ownership
- no AI/trading/risk/signal/regime/portfolio logic
- no vendor calls outside `--live-check`

## Operator use

Use this for explicit ETF/index symbols after the ETF/index universe foundation has been staged and before any broader expansion work.
