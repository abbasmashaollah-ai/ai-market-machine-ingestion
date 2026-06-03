# Volatility Index Live Check Blocked

The volatility index live-check path is currently blocked for Polygon index observations until the manual readiness command confirms access.

Observed result:
- `VIX` returned `403`
- `VVIX` returned `403`
- `VXN` returned `403`
- `RVX` returned `403`

Safety boundary:
- no DB writes
- no scheduler
- no persistence approved
- no secrets exposure

Why this remains blocked:
- the current Polygon path cannot fetch the VIX-family symbols under the current entitlement
- the live dry run produced no accepted observations
- writer and persistence must stay blocked until a valid source is confirmed
- the blocked state applies to the writer handoff boundary as well as the persistence boundary

Next option:
- confirm whether a Polygon entitlement upgrade or plan change is available
- if an alternate vendor already exists in repo, validate whether it can cover all four symbols with stable lineage and source attribution
- otherwise continue with source research before any write-capable step

Next option:
- run `scripts/volatility_live_source_dry_run.py --confirm-live` manually
- interpret `entitlement_failure` or `rate_limited` as a vendor access block
- decide between Cboe source research or a Polygon plan upgrade decision after the readiness check
