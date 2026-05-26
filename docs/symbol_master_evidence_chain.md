# Symbol Master Evidence Chain

`scripts/verify_symbol_master_evidence_chain.py` is the read-only evidence verifier for the symbol master manual confirmed-write path.

## Behavior

- requires `DATABASE_URL`
- reads `public.symbol_master` only
- reports `row_count`, `active_count`, and `inactive_count`
- optionally checks a single `--symbol`
- reports `symbol_found=true|false` when a symbol is provided
- optional `--record-run`, `--record-quality`, and `--record-lineage` persist approved generic store rows when `DATABASE_URL` is present
- emits PASS / WARN / FAIL output without writing to the database
- reports `run_status`, `quality_status`, and `lineage_status`

## Boundary

- no vendors
- no migrations
- no schema ownership
- no FastAPI routes
- no scheduler activation
- no AI/trading/risk/signal/regime/portfolio logic

## Operator use

Run this after a manual confirmed-write to confirm the symbol master table reflects the expected rows.
