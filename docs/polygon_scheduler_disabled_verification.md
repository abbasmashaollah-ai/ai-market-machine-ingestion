# Polygon Scheduler Disabled Verification

`scripts/verify_polygon_scheduler_disabled.py` is a read-only diagnostic that confirms the Polygon OHLCV scheduler stub is disabled by default.

## What it verifies

- `ENABLE_POLYGON_OHLCV_SCHEDULER` is not set to `true`
- the explicit enable flag is required
- the default scheduler status remains `scheduler_disabled`
- Railway startup remains safe because the scheduler does not activate on its own

## Safety

The verifier does not:

- call Polygon
- require `DATABASE_URL`
- require `POLYGON_API_KEY`
- write to the database
- execute the scheduler in enabled mode

`ai-market-machine-data` remains the schema owner.
