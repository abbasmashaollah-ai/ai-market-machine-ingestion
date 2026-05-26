# Symbol Master Source Plan

This document describes the planned source candidates for future symbol master coverage.

## Source candidates

- FMP
- Polygon
- SEC
- Nasdaq/official listings
- manual fixture

## Boundary

- planning only
- no live vendor calls
- no DB writes
- no scheduler activation
- no FastAPI routes
- no AI/trading/risk/signal/regime/portfolio logic

## Notes

- FMP and Polygon are the first planned candidates for future large-scale US ticker coverage.
- SEC is a later enrichment source.
- Manual fixture remains test/dry-run only.
