# Flows/Positioning Source Plan

This document describes the planned source candidates for flows and positioning coverage.

## Source candidates

- FMP
- FINRA
- CFTC
- ETF issuer/public datasets
- vendor_flow_feed
- manual_fixture

## Candidate notes

FMP is the primary planned vendor source for broad flows and positioning coverage if approved later.
FINRA is the planned source for short-interest and off-exchange volume data where publicly available.
CFTC is the planned source for futures positioning and COT-style reports if approved later.
ETF issuer/public datasets are the planned public path for ETF and fund flow context.
vendor_flow_feed is a placeholder for a future specialized vendor flow product.
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

- Supported datasets are `ETF flows`, `fund flows`, `short interest`, `institutional positioning`, `CFTC/COT positioning`, and `dark pool/off-exchange volume`.
- Symbol master and the ETF/index universe are the upstream dependencies.
- Lineage must preserve source identifiers and symbol mappings where available.
