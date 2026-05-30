# News/Sentiment Source Plan

This document describes the planned source candidates for news and sentiment coverage.

## Source candidates

- Finnhub
- FMP
- Polygon
- manual_fixture

## Candidate notes

Finnhub is the primary planned source for broad news coverage and vendor-provided sentiment if approved.
FMP is the planned complementary vendor source for market news and related-ticker coverage.
Polygon is the planned news source if entitlement and availability are approved.
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

- Supported record shape fields are `news_id`, `published_at`, `source`, `publisher`, `title`, `summary`, `url`, `tickers`, `sentiment_label`, `sentiment_score`, `raw_source_id`, and `notes`.
- Symbol master is the required upstream dependency for ticker mapping.
- Lineage must preserve source identifiers and request context where available.
