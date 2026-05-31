# Flows/Positioning Readiness Summary

The flows/positioning vertical slice is currently at readiness checkpoint, not at persistence.

## Ready Items

- vertical-slice plan exists
- source plan exists
- fixture-backed dry-run foundation exists
- preflight exists
- evidence plan exists
- manual inventory includes flows/positioning commands

## Datasets Covered

- ETF flows
- fund flows
- short interest
- institutional positioning
- CFTC/COT positioning
- dark pool/off-exchange volume

## Dependencies and Candidates

- symbol_master is the upstream dependency
- ETF/index universe is the upstream dependency
- source candidates include FMP, FINRA, CFTC, ETF issuer/public datasets, vendor_flow_feed, and manual_fixture

## Current Boundary

- live adapters are not built yet
- data-side contracts are not yet approved
- persistence is deferred
- no DB reads or DB writes are enabled

## Next Options

- data-side flows/positioning contract
- FINRA short-interest live dry-run planning
- CFTC/COT live dry-run planning
- ETF issuer flow-source research

## Boundary Statement

This repository remains on the producer-planning side only.
No AI/trading/risk/signal/regime/portfolio logic belongs in this readiness checkpoint.
