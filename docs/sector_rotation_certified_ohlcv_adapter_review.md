# Sector Rotation Certified OHLCV Adapter Review

## Purpose

This review checks whether `ai-market-machine-ingestion` already has an approved data-read/private-read client path that can feed the sector rotation reader from certified OHLCV data.

The result of this review determines whether a runtime adapter can proceed now or whether a new data-read client contract must be created first.

## Current Reader Transformer Status

The sector rotation reader now has a pure certified OHLCV row-to-history transformer.
The sector rotation certified OHLCV adapter now exists as mocked/test-only runtime code that uses `DataReadClient`, but live endpoint verification has not been done.
The live route is now confirmed as single-symbol: `GET /internal/read/symbol/{symbol}/ohlcv/history`.
The adapter now fans out per required symbol and combines each symbol's `historical_ohlcv` rows before the dry-run pipeline.

It already shapes certified OHLCV rows into the existing dry-run input:

```python
price_history_by_symbol = {"SPY": [...], "XLK": [...], ...}
```

That transformer is transformation-only and does not call vendors, write to the database, or calculate sector features.

## Existing Client/Read Support Found in Repo

Searches across `app/`, `docs/`, `scripts/`, and `tests/` found:

- OHLCV writer and ingestion support
- Polygon vendor clients
- FMP vendor clients
- manual OHLCV runtime and checkpoint tooling
- read-only diagnostics that query `canonical_ohlcv` through direct database access
- planning docs that mention certified/approved data ownership in `ai-market-machine-data`

No approved `DataReadClient` or dedicated private-read client implementation was found in this repository.

## Approved DataReadClient / Private-Read Path

The shared read contract is documented in `docs/data_read_client_contract.md`, and a first mocked `DataReadClient` implementation now exists in `app/clients/data_read_client.py`.

That implementation is test-proven only. The live endpoint has now been confirmed manually, but the sector rotation runtime adapter remains mock/test-only until the private-read endpoint, auth, and response shape are fully approved for runtime use.

The adapter should call `get_symbol_ohlcv_history(...)` once per required symbol and combine the `historical_ohlcv` rows.

## What Exists Instead

The repo currently has:

- vendor clients for upstream data fetches
- direct DB writer paths for approved producer writes
- direct DB read diagnostics for operational verification
- source planning surfaces

Those are not the same thing as a warehouse-owned or private-read client contract for certified OHLCV consumption.

## Required Endpoint Behavior

The future reader endpoint or client must:

- read certified historical OHLCV for `SPY` plus the 11 SPDR sector ETFs
- return close history and quality/certification/freshness metadata
- remain read-only
- avoid vendor access
- keep the feature pipeline unchanged

## Proposed Adapter Responsibility

If an approved data-read client appears, the sector rotation adapter should:

- call the approved data-read client
- request the required symbols and a suitable lookback window
- normalize and shape rows through `build_price_history_by_symbol(...)`
- return the reader result and warnings

The symbol set includes `SPY`, `XLC`, `XLY`, `XLP`, `XLE`, `XLF`, `XLV`, `XLI`, `XLB`, `XLRE`, `XLK`, and `XLU`.

The auth/token boundary should be explicit, for example via `X-Ops-Internal-Token` or an equivalent approved auth/token mechanism.

The adapter should not calculate sector returns or relative strength. Those remain in the feature layer.

## Risks

- contract drift between the data-read client and the reader transformer
- unclear auth/token boundary for the private-read path
- uncertainty around the exact lookback window needed for 60d returns
- ambiguity over adjusted close versus plain close
- hidden dependencies on data quality and freshness semantics

## Non-Goals

This review does not include:

- runtime client implementation
- no vendor calls
- no DB writes
- read-only
- no real writer
- no scheduler activation
- AI Machine logic
- `ai-market-machine-data` changes

## Recommended Next Step

Confirm the live private-read endpoint, auth header, response shape, and secret handling before enabling any sector rotation runtime adapter beyond mocked tests.

The live verification plan is documented in `docs/sector_rotation_certified_ohlcv_live_read_plan.md`.
