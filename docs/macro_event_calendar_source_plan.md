# Macro Event Calendar Source Plan

This document describes the planned source candidates for CPI, FOMC, and NFP event-calendar coverage.
It is planning only and does not enable persistence.

## Source Candidates

- BLS CPI
- Federal Reserve FOMC
- BLS NFP
- manual_fixture

## Candidate Notes

BLS is the preferred public source for CPI and NFP planning.
The Federal Reserve is the preferred public source for FOMC planning.
The manual fixture is test-only and exists for deterministic dry-run coverage.

## Contract Alignment

Source candidates must continue to align with the approved canonical event calendar contract:

- `event_id`
- `event_type`
- `event_date`
- `event_time`
- `timezone`
- `source`
- optional `symbol`
- `title`
- `importance`
- `notes`

## Timezone and Time Handling

- `timezone` should normalize to `America/New_York` for US macro events.
- `event_time` must be preserved when present.
- If the upstream source omits a precise time, keep the release window explicit instead of inventing a fake timestamp.

## Source and Lineage Expectations

- preserve source labels in normalized records
- preserve upstream identifiers where available
- keep lineage traceable to the original macro source or fixture

## Boundary

- planning only
- no live vendor calls
- no DB writes
- no scheduler activation
- no FastAPI routes
- no AI/trading/risk/signal/regime/portfolio logic
- no persistence until the data-side table and writer boundary are approved

