# Options Readiness Summary

The options vertical slice is currently at readiness checkpoint, not at persistence.

## Ready Items

- vertical-slice plan exists
- source plan exists
- fixture-backed dry-run foundation exists
- preflight exists
- evidence plan exists
- manual inventory includes options commands

## Datasets Covered

- option chains
- option contracts
- open interest
- implied volatility
- put/call volume
- put/call open interest
- expiration metadata

## Dependencies and Candidates

- symbol_master is the upstream dependency
- source candidates include Polygon, Tradier, OCC-derived, and manual_fixture

## Current Boundary

- live adapters are not built yet
- data-side contracts are not yet approved
- persistence is deferred
- no DB reads or DB writes are enabled

## Next Options

- data-side options contract
- Polygon options live dry-run planning
- Tradier live dry-run planning
- OCC-derived metadata planning

## Boundary Statement

This repository remains on the producer-planning side only.
No AI/trading/risk/signal/regime/portfolio logic belongs in this readiness checkpoint.
