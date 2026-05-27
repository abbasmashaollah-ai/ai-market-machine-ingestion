# Earnings Calendar Source Plan

This document describes the planned source candidates for earnings-date coverage.
It is planning only and does not enable persistence.

## Source Candidates

- FMP
- Finnhub
- Nasdaq
- manual_fixture

## Candidate Notes

FMP is a likely primary source for earnings-date coverage when vendor access is approved.
Finnhub is a likely supplementary source.
Nasdaq is a likely public or vendor-backed source for earnings calendar coverage.
The manual fixture is test-only and exists for deterministic dry-run coverage.

## Contract Alignment

Source candidates must continue to align with the approved canonical event calendar contract:

- `event_id`
- `event_type`
- `event_date`
- `event_time`
- `timezone`
- `source`
- `symbol`
- `title`
- `importance`
- `notes`

## Timezone and Time Handling

- `timezone` should normalize to the market or exchange local timezone when available.
- `event_time` should be preserved when present.
- If the upstream source omits a precise time, keep the release window explicit instead of inventing a fake timestamp.

## Source and Lineage Expectations

- preserve source labels in normalized records
- preserve upstream identifiers where available
- keep lineage traceable to the original earnings source or fixture

## Boundary

- planning only
- no live vendor calls
- no DB reads
- no DB writes
- no scheduler activation
- no FastAPI routes
- no AI/trading/risk/signal/regime/portfolio logic
- no persistence until the data-side table and writer boundary are approved

