# Breadth/Participation Source Plan

This document describes the planned source candidates for breadth and participation coverage.

## Source candidates

- vendor_breadth_feed
- exchange_breadth_feed
- derived_from_ohlcv
- manual_fixture

## Candidate notes

vendor_breadth_feed is the planned vendor source for breadth metrics if an approved market data source exists.
exchange_breadth_feed is the planned exchange feed where direct exchange data is available.
derived_from_ohlcv is the planned derived path from approved OHLCV data once the OHLCV contract exists.
manual_fixture is test-only and exists for deterministic planning coverage.

## Boundary

- planning only
- no live vendor calls
- no DB reads
- no DB writes
- no scheduler activation
- no FastAPI routes
- no AI/trading/risk/signal/regime/portfolio logic

## Notes

- Supported metrics are `advance/decline counts`, `new highs/new lows`, `percent above moving averages`, `up-volume/down-volume`, `sector participation`, and `index/universe breadth`.
- Symbol master and the ETF/index universe are the upstream dependencies.
- Lineage must preserve source identifiers and universe mappings where available.
