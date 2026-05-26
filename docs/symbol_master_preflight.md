# Symbol Master Preflight

`scripts/preflight_symbol_master_operations.py` is the read-only operator preflight for the symbol master manual workflow.

## Checks

- manual command inventory includes the symbol master runner
- manual command inventory includes the Polygon symbol master runner
- `app.writers.symbol_master_writer.SymbolMasterWriter` exists
- symbol-master docs exist
- `DATABASE_URL` is required only for `--confirm-write` or `--check-existing`
- `POLYGON_API_KEY` is required only for `scripts/dry_run_polygon_symbol_master.py --live-check`
- `--record-run`, `--record-quality`, and `--record-lineage` require `DATABASE_URL` and the confirmed live Polygon path
- forbidden imports are absent from the symbol master command and writer paths
- the data-owned symbol master schema is referenced by table contract, not by data-repo internals

## Boundary

- read-only only
- no vendor calls
- no DB writes
- no migrations
- no scheduler activation
- no FastAPI routes
- no AI/trading/risk/signal/regime/portfolio logic
