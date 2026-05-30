# Cross-Asset OHLCV Readiness Summary

The cross-asset OHLCV vertical slice is currently at readiness checkpoint, not at persistence.

## Ready Items

- vertical-slice plan exists
- source plan exists
- fixture-backed dry-run foundation exists
- preflight exists
- evidence plan exists
- manual inventory includes cross-asset OHLCV commands

## Target Asset Groups

- bonds/rates proxies
- DXY / dollar index proxy
- commodities
- crypto
- FX

## Dependencies and Candidates

- symbol_master or a separate asset-master dependency is required upstream
- source candidates include Polygon, FMP, manual_fixture, and a future specialty FX/crypto path

## Current Boundary

- live vendor adapters are not built yet
- data-side asset scope is not yet approved
- persistence is deferred
- no DB reads or DB writes are enabled

## Next Options

- data-side asset-scope contract
- Polygon cross-asset live dry-run planning
- specialty FX/crypto source research

## Boundary Statement

This repository remains on the producer-planning side only.
No AI/trading/risk/signal/regime/portfolio logic belongs in this readiness checkpoint.
