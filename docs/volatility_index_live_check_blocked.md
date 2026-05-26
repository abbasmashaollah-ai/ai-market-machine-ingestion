# Volatility Index Live Check Blocked

The volatility index live-check path is currently blocked for Polygon index observations.

Observed result:
- `VIX` returned `401`
- `VXN` returned `401`

Safety boundary:
- no DB writes
- no scheduler
- no persistence approved

Next option:
- Cboe source research
- or a Polygon plan upgrade decision
