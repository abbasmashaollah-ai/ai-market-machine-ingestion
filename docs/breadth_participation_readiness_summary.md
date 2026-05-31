# Breadth/Participation Readiness Summary

The breadth/participation vertical slice is currently at readiness checkpoint, not at persistence.

## Ready Items

- vertical-slice plan exists
- source plan exists
- fixture-backed dry-run foundation exists
- preflight exists
- evidence plan exists
- manual inventory includes breadth/participation commands

## Metric Types Covered

- `advance_decline_count`
- `new_highs_new_lows`
- `percent_above_moving_average`
- `up_down_volume`
- `sector_participation`
- `index_universe_breadth`

## Dependencies and Candidates

- symbol_master is the upstream dependency
- ETF/index universe is the upstream dependency
- source candidates include vendor breadth feeds, exchange breadth feeds, derived-from-OHLCV, and manual_fixture

## Current Boundary

- live vendor adapters are not built yet
- data-side contracts are not yet approved
- persistence is deferred
- no DB reads or DB writes are enabled

## Next Options

- data-side breadth contract
- derived-from-OHLCV planning
- vendor/exchange breadth source research

## Boundary Statement

This repository remains on the producer-planning side only.
No AI/trading/risk/signal/regime/portfolio logic belongs in this readiness checkpoint.
