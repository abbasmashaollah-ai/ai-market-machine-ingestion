# Writer Contracts

The writer layer defines interfaces and result contracts for future canonical writes.

## Scope

This layer provides:

- a canonical writer protocol
- writer result dataclasses
- batch summary helpers
- placeholder writers for OHLCV, macro, symbol, and lineage-related contracts

## Boundary

This layer does not:

- execute SQL
- write to the database
- create tables
- run migrations
- use SQLAlchemy sessions for persistence
- call vendor APIs
- run ingestion pipelines
- run backfills
- start schedulers
- expose API routes
- perform AI or trading logic

## Design Notes

- Placeholder writers raise `NotImplementedError` to make the boundary explicit.
- The result contracts are intended to support future approved persistence without defining database behavior here.
