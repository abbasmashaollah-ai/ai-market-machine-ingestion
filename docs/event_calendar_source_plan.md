# Event Calendar Source Plan

This document describes the planned source candidates for event calendar coverage.

## Source candidates

- FRED/BLS/Fed official sources
- exchange/calendar/manual rule source
- FMP/Finnhub/Nasdaq
- manual fixture

## Candidate notes

FRED/BLS/Fed official sources are the leading planned sources for CPI, FOMC, and NFP-style macro events.
The exchange/calendar/manual rule source is the deterministic path for OPEX.
FMP/Finnhub/Nasdaq are the planned earnings calendar sources if vendor access is approved.
The manual fixture remains test-only and exists for deterministic planning coverage.

## Boundary

- planning only
- no live vendor calls
- no DB writes
- no scheduler activation
- no FastAPI routes
- no AI/trading/risk/signal/regime/portfolio logic

## Notes

- Supported event types are `CPI`, `FOMC`, `NFP`, `OPEX`, and `earnings_date`.
- Timezone handling must be normalized before any persistence work is considered.
