# Macro Event Calendar Plan

This document defines the planning boundary for CPI, FOMC, and NFP event-calendar work.
It is planning only and does not enable persistence.

## Event Types

- `CPI`
- `FOMC`
- `NFP`

## Likely Sources

- BLS for CPI and NFP
- Federal Reserve for FOMC
- manual fixture for tests

## Contract Alignment

Normalized records must continue to align with the approved canonical event calendar contract:

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

- `event_time` must be preserved when present.
- `timezone` must be explicit when time is present.
- deterministic planning should keep timezone normalization stable for downstream validation.

## Source and Lineage Expectations

- preserve source labels in normalized records
- preserve upstream event identifiers where available
- keep lineage traceable to the original macro source or fixture

## Boundary

No persistence is allowed until the data-side table and writer boundary are approved.
No AI/trading/risk/signal/regime/portfolio logic belongs in this plan.

