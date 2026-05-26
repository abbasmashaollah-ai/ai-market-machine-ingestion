# Volatility Index Source Plan

This document describes the planned source candidates for volatility index coverage.

## Source candidates

- Polygon
- Cboe
- manual fixture

## Candidate notes

Polygon is the leading planned source for broader coverage, but it remains unapproved here.
Cboe is a later approved-source candidate for Cboe-family volatility indexes.
The manual fixture remains test-only and exists for deterministic planning coverage.

## Boundary

- planning only
- no live vendor calls
- no DB writes
- no scheduler activation
- no FastAPI routes
- no AI/trading/risk/signal/regime/portfolio logic

## Notes

- Supported starter symbols are `VIX`, `VVIX`, `VXN`, and `RVX`.
- Vendor-symbol mapping is intentionally documented before any live adapter work.
