# FRED Vendor Foundation

This document covers the FRED-specific vendor foundation in `app/vendors/fred/`.

## Scope

The FRED foundation provides:

- endpoint and query builders
- lightweight FRED payload dataclasses
- pure mapping helpers into normalized internal records
- a FRED client interface and transport-wired safe placeholder

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
- add other FRED product areas such as other data services or downstream analytics

## Design Notes

- Endpoint helpers are pure string builders.
- The client uses the shared HTTP transport dependency when provided, but still returns raw payloads only.
- Mapping helpers are pure and reuse internal normalized macro models and common parsing helpers.
