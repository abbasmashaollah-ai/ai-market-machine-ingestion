# Volatility Index Live Dry Run

`scripts/dry_run_volatility_index_foundation.py` is the manual operator command for the volatility index foundation.

## Behavior

- default mode uses a deterministic fixture
- `--live-check` fetches Polygon volatility observations when `POLYGON_API_KEY` is present
- live-check normalizes into `NormalizedVolatilityIndexRecord`
- `I:VIX`, `I:VVIX`, `I:VXN`, and `I:RVX` are normalized back to `VIX`, `VVIX`, `VXN`, and `RVX`
- Polygon index symbols may require plan entitlement
- current observed result: `I:VIX` and `I:VXN` returned `401` on the current key
- `--symbol` can be repeated for starter symbols
- `--max-observations` keeps the newest observations first
- `--show-values` prints normalized values
- `--sleep-seconds-between-symbols` controls live-request pacing
- `--stop-on-rate-limit` and `--no-stop-on-rate-limit` control the rate-limit boundary
- `--max-rate-limit-failures` caps repeated rate-limit failures
- no DB writes
- no scheduler activation
- no FastAPI routes
- no AI/trading/risk/signal/regime/portfolio logic

## Output

- `requested_symbols`
- `normalized_count`
- `valid_count`
- `invalid_count`
- `latest_observation_dates`
- `rate_limit_detected`
- `entitlement_blocked`
- `invalid_records` include safe failure reasons when Polygon returns no usable payload
- `no_db_writes=true`

## Boundary

Polygon live-check usage requires `POLYGON_API_KEY`.
Persistence remains blocked until a valid source is confirmed.
The command does not own schema contracts.
