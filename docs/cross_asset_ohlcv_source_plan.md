# Cross-Asset OHLCV Source Plan

This document describes the planned source candidates for cross-asset OHLCV coverage.

## Source candidates

- Polygon
- FMP
- future_specialty_fx_crypto_source
- manual_fixture

## Candidate notes

Polygon is the primary planned source for broad cross-asset OHLCV coverage if approved later.
FMP is the complementary planned source where suitable symbols are available.
future_specialty_fx_crypto_source is a placeholder for later FX/crypto planning only.
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

- Target groups are `bonds/rates proxies`, `DXY / dollar index proxy`, `commodities`, `crypto`, and `FX`.
- Symbol master or a separately approved asset-master planning path is the upstream dependency.
- Lineage must preserve vendor symbol mappings and market-date context where available.
