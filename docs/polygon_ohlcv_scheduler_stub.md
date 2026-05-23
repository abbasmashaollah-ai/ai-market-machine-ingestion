# Polygon OHLCV Scheduler Stub

`scripts/run_polygon_ohlcv_scheduler_cycle.py` is a disabled-by-default scheduler boundary.

## Behavior

The stub prints `status=scheduler_disabled` unless both conditions are met:

- `--enable-scheduler-cycle`
- `ENABLE_POLYGON_OHLCV_SCHEDULER=true`

When enabled, it runs the existing preflight first and blocks on a blocked preflight. It only hands off to the existing daily runner for symbols that are already safe to run manually.

## Safety

The stub does not:

- run on Railway startup
- register cron
- call Polygon unless explicitly enabled
- write to the database unless explicitly enabled and the existing runner options request it
- add API routes
- add AI, trading, risk, signal, regime, portfolio, strategy, or prediction logic

`ai-market-machine-data` remains the schema owner.
