# Manual OHLCV Preflight

`scripts.preflight_polygon_ohlcv_operations.py` and `scripts.preflight_fmp_ohlcv_operations.py` provide read-only preflight checks for manual OHLCV operations.

## Scope

These commands verify:

- required vendor environment for the selected command path
- `DATABASE_URL` only when `--check-existing` or evidence-recording flags require it
- command inventory availability
- shared evidence-verifier semantics
- boundary guardrails for manual command paths
- request-budget estimates are within the configured cap

## Vendor-specific behavior

- Polygon preflight retains the existing universe, existing-coverage, and backfill recommendation behavior.
- FMP preflight checks manual daily-update readiness with the same inventory and evidence semantics.

## Safety

These preflights do not:

- expose API routes
- own migrations
- own schemas
- introduce AI/trading/risk/signal/regime/portfolio logic
- schedule work
- call vendors unless a vendor-specific check explicitly requires it

The commands remain operator-run only.

The scheduler readiness assessor (`scripts.assess_ohlcv_scheduler_readiness.py`) consumes these preflights as part of a read-only readiness check. It does not activate a scheduler.
