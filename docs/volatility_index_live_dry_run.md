# Volatility Index Live Dry Run

`scripts/volatility_live_source_dry_run.py` is the manual operator command for live-source readiness checks on VIX-family volatility observations.

## Behavior

- manual-only command
- requires `--confirm-live` before any live Polygon call can happen
- defaults to `VIX`, `VVIX`, `VXN`, and `RVX`
- maps to `I:VIX`, `I:VVIX`, `I:VXN`, and `I:RVX`
- fetches through the existing Polygon adapter only when explicitly confirmed
- passes fetched records through the dry-run volatility observations producer
- prints a safe summary with requested symbols, fetched count, accepted count, rejected count, warnings, and error categories
- no DB writes
- no scheduler activation
- no persistence
- no AI/trading/risk/signal/regime/portfolio logic

## Output

- `requested_symbols`
- `fetched_count`
- `accepted_count`
- `rejected_count`
- `warnings`
- `error_categories`
- `no_db_writes=true`
- `no_scheduler_activation=true`
- `no_persistence=true`
- polygon live-check usage requires `POLYGON_API_KEY`

## Entitlement Interpretation

- `rate_limited` indicates the vendor path was throttled
- `entitlement_failure` indicates the vendor path is blocked by access policy or plan limits
- `vendor_error` indicates a non-entitlement vendor failure
- the command must not print API keys or other secrets

## Observed Live Dry Run

The most recent confirmed live dry run returned the following result for `VIX`, `VVIX`, `VXN`, and `RVX`:

- `requested_symbols=['VIX', 'VVIX', 'VXN', 'RVX']`
- `fetched_count=0`
- `accepted_count=0`
- `rejected_count=0`
- warnings:
  - `VIX: unexpected http status: 403`
  - `VVIX: unexpected http status: 403`
  - `VXN: unexpected http status: 403`
  - `RVX: unexpected http status: 403`
- `error_categories=['vendor_error']`
- `no_db_writes=true`
- `no_scheduler_activation=true`
- `no_persistence=true`

## Boundary

The command is a readiness check only.
Persistence remains blocked until the live source can be confirmed and a writer boundary is approved.
