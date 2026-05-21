# Polygon Vendor Foundation

This document covers the Polygon-specific vendor foundation in `app/vendors/polygon/`.

## Scope

The Polygon foundation provides:

- endpoint path builders
- lightweight Polygon payload dataclasses
- pure mapping helpers into normalized internal records
- a thin rate-limiter wrapper
- a deterministic retry policy contract
- a Polygon client interface and safe placeholder

## Boundary

This foundation does not:

- perform live HTTP calls by default
- execute ingestion pipelines
- write to the database
- implement writers
- run backfills
- start schedulers
- expose API routes
- perform AI or trading logic
- add other Polygon product areas such as news, options, or fundamentals

## Design Notes

- Endpoint helpers are pure string builders.
- The client placeholder raises `NotImplementedError` to keep execution out of this layer.
- Mapping helpers are pure and reuse internal normalized models and common parsing helpers.
