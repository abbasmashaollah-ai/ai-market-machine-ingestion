# Macro Event Calendar Foundation

This document describes the fixture-backed macro event calendar foundation.
It is documentation and dry-run planning only.

## Scope

- CPI, FOMC, and NFP only
- fixture-backed dry-run planning only
- no vendor calls
- no DB writes
- no scheduler
- no FastAPI routes
- no migrations
- no schema ownership
- no AI/trading/risk/signal/regime/portfolio logic

## Fixture Records

The deterministic fixture set includes:

- `CPI`
- `FOMC`
- `NFP`

Each record aligns with the canonical event calendar contract:

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

## Contract Rules

- `source` is `manual_fixture`
- `timezone` is `America/New_York`
- `importance` is `high`
- `event_id` uses a stable `EVENTTYPE-YYYY-MM-DD` format
- `event_time` is preserved when present
- `timezone` must remain explicit when time is present
- source and lineage information must remain traceable to the fixture or upstream macro source

## Dry-Run Contract

The dry-run command reports:

- `event_count`
- `normalized_count`
- `valid_count`
- `invalid_count`
- `event_types`
- `no_vendor_calls=True`
- `no_db_writes=True`

Optional flags:

- `--event-type`
- `--show-events`
- `--show-invalid`

## Boundary

No persistence is allowed until the data-side table and writer boundary are approved.
No AI/trading/risk/signal/regime/portfolio logic belongs in this foundation.

