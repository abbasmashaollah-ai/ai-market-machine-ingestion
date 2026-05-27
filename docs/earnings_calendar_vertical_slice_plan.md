# Earnings Calendar Vertical Slice Plan

This document defines the planning boundary for the earnings calendar subdomain.
It is documentation only and does not enable persistence.

## Purpose

- provide a separate event-calendar subdomain for earnings date planning
- keep earnings-date records data-only and aligned to the canonical event calendar contract
- preserve a clean producer boundary before any future live adapter is approved

## Event Type

- `event_type=earnings_date`

## Dependency

- `symbol_master` is required for symbol validation and canonical symbol mapping before any future writer boundary is approved

## Likely Sources

- FMP
- Finnhub
- Nasdaq
- manual_fixture for tests

## Normalized Record Shape

Records must align with the canonical event calendar contract:

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

## Time Handling

- `event_time` may be unknown for some earnings dates
- when unknown, keep the field explicit as null instead of inventing a timestamp
- `timezone` must remain explicit when an event time is present
- preserve the source-provided release window or note when only a date is available

## Source and Lineage Expectations

- preserve the upstream source label in normalized records
- preserve upstream identifiers when available
- keep symbol, date, time, and title traceable to the source or fixture

## Quality Expectations

- validate symbols against `symbol_master` when available
- maintain deterministic fixture behavior in tests
- do not silently widen the event type beyond `earnings_date`
- surface missing time or incomplete source coverage explicitly

## Preflight / Runner / Evidence Pattern

- preflight should remain read-only
- runner commands should remain dry-run only until a writer boundary is approved
- evidence checks should stay deferred until the persistence contract exists

## Boundary

No persistence is allowed until the data-side table and writer boundary are approved.
No vendor calls, DB reads, DB writes, scheduler behavior, FastAPI routes, migrations, schema ownership, AI, trading, risk, signal, regime, or portfolio logic belong here.

