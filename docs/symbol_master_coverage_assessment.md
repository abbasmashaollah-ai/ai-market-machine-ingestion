# Symbol Master Coverage Assessment

`scripts/assess_symbol_master_coverage.py` is the read-only symbol-master coverage and reconciliation check.

## Behavior

- requires `DATABASE_URL`
- reads `public.symbol_master` only
- supports optional `--vendor`, `--exchange`, `--asset-type`, and `--active` filters
- reports `total_rows`, `active_rows`, `inactive_rows`
- reports counts by exchange and asset type
- reports missing `vendor_symbol`, `exchange`, and `asset_type` counts
- reports duplicate symbol count when duplicates are detectable from the loaded rows
- emits `coverage_status=PASS|WARN|FAIL`

## Thresholds

- `--min-total`
- `--min-active`
- `--max-missing-exchange-ratio`
- `--max-missing-asset-type-ratio`

## Boundary

- read-only only
- no vendors
- no DB writes
- no migrations
- no schema ownership
- no scheduler activation
- no FastAPI routes
- no AI/trading/risk/signal/regime/portfolio logic
