# Cross-Asset OHLCV Evidence Plan

This is the evidence planning layer for the future persistence contract.

Planned checks after persistence exists:
- row counts by `asset_group`
- row counts by `symbol`
- missing asset groups
- missing symbol coverage
- missing OHLC values
- stale `market_date` checks
- run/quality/lineage once persistence exists

Current boundary:
- no DB reads yet
- no DB writes yet
- the symbol/asset scope must be approved before evidence-store wiring is added
- the writer plan is deferred and does not enable persistence
