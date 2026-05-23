# Polygon Flat-File End-to-End Readiness

This document rolls up the flat-file planning gates into one operator-facing summary.

## Source split

- `polygon/api` is the current live path for recent and daily data
- `polygon/flatfiles` is the future historical and backfill path
- `polygon/websocket` is the future live-streaming path

## Readiness areas

- official layout
- config
- storage policy
- discovery
- download
- manifest
- integrity
- quarantine
- parse
- persistence

## Status

- `flatfile_e2e_status=planning_only_not_enabled`
- `live_flatfile_pipeline_enabled=false`

## Safety

This summary does not:

- call Polygon
- call S3
- download files
- read files
- write files
- write to the database
- add scheduler behavior
- add API routes
- add AI, trading, risk, signal, regime, portfolio, strategy, or prediction logic

`ai-market-machine-data` remains the schema owner.
