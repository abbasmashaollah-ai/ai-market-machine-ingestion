# Polygon Preflight Recommendation Verification

`scripts/verify_polygon_preflight_recommendations.py` checks the structural safety of the commands emitted by `scripts/preflight_polygon_ohlcv_operations.py`.

## Scope

The verifier is manual and read-only. It reuses the preflight planning logic, inspects the generated `recommended_command` strings, and rejects unsafe command shapes before an operator runs anything.

## Safety checks

The verifier rejects commands that:

- contain `DATABASE_URL`
- contain `POLYGON_API_KEY`
- contain `--confirm-write`
- do not start with `python -m scripts.`
- target a module outside the allowlist

Allowed command targets are:

- `scripts.run_polygon_ohlcv_daily_update`
- `scripts.run_polygon_ohlcv_chunked_backfill`
- `scripts.verify_polygon_ohlcv_evidence_chain`
- `scripts.fill_polygon_ohlcv_gaps`

`ai-market-machine-data` remains the schema owner.
