# Symbol Master Contracts

The symbol master layer defines validation, universe, sync planning, and service contracts for future symbol resolution work.

## Scope

This layer provides:

- symbol record validation helpers
- universe request dataclasses and label helpers
- a symbol master service protocol and safe placeholder
- symbol sync planning dataclasses

## Boundary

This layer does not:

- perform real symbol sync
- call Polygon, FMP, Finnhub, or SEC APIs
- write to the database
- implement writers
- run ingestion pipelines
- run backfills
- start schedulers
- expose API routes
- perform AI or trading logic

## Design Notes

- Universe names are labels only and remain internal planning inputs.
- The service placeholder raises `NotImplementedError` to keep the boundary explicit.
- Validation is in-memory and uses normalized symbol records only.
