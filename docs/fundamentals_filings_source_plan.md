# Fundamentals/Filings Source Plan

This document describes the planned source candidates for fundamentals and filings coverage.

## Source candidates

- SEC
- FMP
- Finnhub
- manual_fixture

## Candidate notes

SEC is the primary planned source for authoritative filing coverage and high-confidence company metadata where available.
FMP is the planned vendor source for statements, ratios, metrics, and estimates if entitlement is approved.
Finnhub is the planned complementary vendor source for broad fundamentals and filing-adjacent coverage.
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

- Supported record families are `company_profile`, `financial_statement`, `financial_metric`, `earnings_estimate`, and `sec_filing`.
- Symbol master is the required upstream dependency before persistence is considered.
- Lineage must preserve source identifiers and request context where available.
