# FRED Client Transport

This document covers the FRED client wiring in `app/vendors/fred/client.py`.

## Scope

The client layer provides:

- raw fetch methods for series observations and series metadata
- shared HTTP transport dependency injection
- request metadata construction through FRED endpoint helpers
- API key forwarding through query parameters

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

- The client returns raw decoded payloads only, with observation payloads preserved as decoded response objects so downstream tools can inspect response keys safely.
- Tests should mock the HTTP transport dependency and must not make live FRED calls.
- API keys are forwarded through query parameters, not embedded in logs or response handling.
