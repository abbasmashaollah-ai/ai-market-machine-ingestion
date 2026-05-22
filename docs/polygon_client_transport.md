# Polygon Client Transport

This document covers the Polygon client wiring in `app/vendors/polygon/client.py`.

## Scope

The client layer provides:

- raw fetch methods for aggregates and tickers
- shared HTTP transport dependency injection
- request metadata construction through Polygon endpoint helpers
- API key forwarding through query parameters
- optional retry and rate-limit hooks
- a transport-backed factory for manual runtime wiring

## Boundary

This layer does not:

- normalize vendor data
- write to the database
- implement writers
- execute ingestion pipelines
- run backfills
- start schedulers
- expose API routes
- perform AI or trading logic

## Design Notes

- The client returns raw decoded payloads only.
- Tests should mock the HTTP transport dependency and must not make live Polygon calls.
- API keys are forwarded through query parameters, not embedded in logs or response handling.
- Manual Polygon runtime commands should use the shared HTTP transport factory when `POLYGON_API_KEY` is present.
