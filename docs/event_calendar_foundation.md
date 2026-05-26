# Event Calendar Foundation

This document describes the dry-run foundation for the event calendar ingestion slice.
It is planning and documentation only.

## Scope

- event calendar only
- dry-run and normalization only
- no vendor calls
- no DB writes
- no scheduler
- no FastAPI routes
- no migrations
- no schema ownership
- no AI/trading/risk/signal/regime/portfolio logic

## Starter Event Types

- `CPI`
- `FOMC`
- `NFP`
- `OPEX`
- `earnings_date`

## Normalized Record Shape

The normalized event calendar record includes:

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

## Dry-Run Contract

The dry-run command uses the deterministic sample fixture by default.
It reports:

- `event_count`
- `normalized_count`
- `valid_count`
- `invalid_count`
- `event_types`
- `no_vendor_calls=True`
- `no_db_writes=True`

Optional flags:

- `--show-events`
- `--show-invalid`
- `--event-type`

## Boundary Statement

The ingestion repo owns producer-side normalization and planning only.
The canonical storage contract belongs in `ai-market-machine-data`.
No AI/trading/risk/signal/regime/portfolio logic belongs in this foundation.
