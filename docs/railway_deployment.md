# Railway Deployment

This repository can deploy to Railway as a safe worker placeholder.

## Runtime entrypoints

- `python -m scripts.railway_start`
- `python -m scripts.railway_healthcheck`

Both commands only verify imports and config shape. They do not trigger ingestion, backfills, schedulers, vendor calls, or database writes.

Manual operator verification commands such as `python -m scripts.verify_manual_ingestion_commands` are separate and are not wired into Railway startup.
The Polygon OHLCV scheduler stub is also not wired into Railway startup; `python -m scripts.verify_polygon_scheduler_disabled` is the read-only check for that guard.

## Health behavior

The healthcheck validates:

- `app` package importability
- `app.core.config.Settings` shape
- `app.core.runtime.RuntimeContext` importability
- `DATABASE_URL` syntax only when the variable is present

The healthcheck does not open a database connection and does not call vendor APIs.

## Railway configuration

`railway.json` uses a safe start command:

`python -m scripts.railway_start`

That command prints a status summary and exits cleanly. It does not execute ingestion jobs or backfills.

## Package entry points

`pyproject.toml` exposes:

- `railway-healthcheck`
- `railway-start`

These entry points mirror the module commands used by Railway.
