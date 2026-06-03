# Data Read Client Contract

## Purpose

This document defines the ingestion-side read-only client contract for certified reads from `ai-market-machine-data`.

The goal is to let ingestion feature modules consume certified warehouse evidence safely without introducing vendor access, write paths, or AI logic into the producer repo.

## Why Ingestion Needs a Read-Only Data Client

Feature modules such as `sector_rotation` need read-only certified inputs from `ai-market-machine-data`.

The ingestion repo should not call vendors for already-certified warehouse evidence.
The ingestion repo should not directly depend on ad hoc DB reads for feature jobs unless that read path is explicitly approved and contracted.

This contract defines the safe, shared way to read certified evidence before any runtime adapter is implemented.

## Three-System Boundary

The boundary remains:

- ingestion reads certified evidence
- data stores and serves certified evidence
- AI Machine interprets evidence

The client defined here belongs to ingestion, but it only reads certified data owned and served by `ai-market-machine-data`.

## Current Blocker

No approved `DataReadClient` / private-read client exists in this repository yet.

That is why runtime adapter work for sector rotation remains blocked.

## Proposed Client Name

`DataReadClient`

## Proposed Package Location

Preferred location:

- `app/clients/data_read_client.py`

If the repo later adopts a more specific client namespace, the contract should remain the same and the module path should remain discoverable from this document.

## Configuration

The client should be configured with:

- `AI_MARKET_MACHINE_DATA_BASE_URL`
- `OPS_INTERNAL_TOKEN` or an equivalent approved secret for private read access
- timeout settings
- retry settings

The client must never print or log secrets.

## Auth

The expected auth mechanism is:

- `X-Ops-Internal-Token` header

The token must never be logged or echoed in diagnostics.

## First Required Method

The first required method should be:

```python
get_symbol_ohlcv_history(symbol, start_date=None, end_date=None, limit=None, order="asc")
```

This method should read certified OHLCV history for a single symbol and date bounds.

## Convenience Method

A convenience method may also exist:

```python
get_certified_ohlcv_history(symbols, start_date=None, end_date=None, lookback_days=None)
```

This method should loop over symbols and combine the single-symbol history rows for consumers such as `sector_rotation`.

## Expected Return Shape

The method should return a list of certified OHLCV rows with fields like:

- symbol
- date or timestamp
- close
- quality_status
- certification_status
- freshness_status
- source or source_attribution
- lineage or evidence if available

The return shape should remain JSON-friendly and stable enough for the sector rotation row transformer.

## Read-Only Behavior

The client must be:

- GET-only
- read-only
- non-mutating
- free of write side effects

It must not write to the database and must not alter any upstream source state.

## Consumers

Initial consumers:

- `sector_rotation`

Later consumers:

- breadth
- price features
- cross_asset

## Error Handling

The client should have explicit behavior for:

- auth failure
- missing symbols
- partial data
- stale or uncertified data
- network timeout
- invalid response shape

Errors should be deterministic and safe to handle without falling back to vendor reads.

## Safety Rules

- no vendor fallback inside `DataReadClient`
- no DB writes
- no AI interpretation
- no scheduler activation
- no token logging

## First Implementation Sequence

1. docs contract
2. fake client fixtures
3. unit tests with mocked responses
4. `DataReadClient` implementation
5. sector rotation adapter using `DataReadClient`
6. no real writer until the read path is proven

Current implementation status:

- `DataReadClient` implementation exists in `app/clients/data_read_client.py`
- tests are mocked only
- live endpoint verification has not been done
- sector rotation adapter remains blocked until the runtime endpoint and response shape are verified
- sector rotation adapter code now exists but remains test-only until the live read endpoint is verified
- `get_symbol_ohlcv_history(...)` exists and is the preferred live-route method

The live verification plan is documented in `docs/data_read_client_live_verification_plan.md`.

## Approval Gates Before Runtime

Before any runtime implementation is enabled, confirm:

- the data endpoint exists
- the auth header is approved
- the response shape is confirmed
- secrets handling is defined
- vendor fallback is not needed

## Non-Goals

This contract does not include:

- runtime HTTP implementation
- vendor calls
- DB writes
- real writer behavior
- scheduler activation
- `ai-market-machine-data` changes
- `AI Machine` changes
