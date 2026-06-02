# Volatility Index Live Check Blocked

The volatility index live-check path is currently blocked for Polygon index observations until the manual readiness command confirms access.

Observed result:
- `VIX` returned `401`
- `VXN` returned `401`

Safety boundary:
- no DB writes
- no scheduler
- no persistence approved
- no secrets exposure

Next option:
- run `scripts/volatility_live_source_dry_run.py --confirm-live` manually
- interpret `entitlement_failure` or `rate_limited` as a vendor access block
- decide between Cboe source research or a Polygon plan upgrade decision after the readiness check
