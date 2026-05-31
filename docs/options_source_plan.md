# Options Source Plan

This document describes the planned source candidates for options coverage.

## Source candidates

- Polygon
- Tradier
- OCC-derived
- manual_fixture

## Candidate notes

Polygon is the primary planned source for broad options coverage if approved later.
Tradier is the complementary planned source where suitable endpoints are available.
OCC-derived is the planned metadata and open-interest backstop path.
manual_fixture is test-only and exists for deterministic planning coverage.

## Boundary

- planning only
- no live vendor calls
- no DB reads
- no DB writes
- no scheduler activation
- no FastAPI routes
- no AI/trading/risk/signal/regime/portfolio logic

## Notes

- Supported datasets are `option chains`, `option contracts`, `open interest`, `implied volatility`, `put/call volume`, `put/call open interest`, and `expiration metadata`.
- Symbol master is the required upstream dependency for underlying symbol normalization.
- Lineage must preserve source identifiers and contract mapping where available.
