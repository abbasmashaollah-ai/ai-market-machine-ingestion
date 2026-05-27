# OPEX Calendar Foundation

This document describes the deterministic OPEX event-calendar slice.
It is planning and dry-run documentation only.

## Scope

- OPEX only
- deterministic third-Friday generation
- dry-run and normalization only
- no vendor calls
- no DB writes
- no scheduler
- no FastAPI routes
- no migrations
- no schema ownership
- no AI/trading/risk/signal/regime/portfolio logic

## Rule

- OPEX candidates are generated as the third Friday of each month.
- The record shape must align with the canonical event calendar contract.
- `event_type` is `OPEX`.
- `source` is `manual_rule`.
- `timezone` is `America/New_York`.
- `importance` is `high`.
- `event_id` is stable and formatted as `OPEX-YYYY-MM-DD`.

## Dry-Run Contract

The dry-run command reports:

- `event_count`
- `normalized_count`
- `valid_count`
- `invalid_count`
- `year`
- `month`
- `no_vendor_calls=True`
- `no_db_writes=True`

Optional flags:

- `--show-events`
- `--show-invalid`

## Boundary Statement

The ingestion repo owns producer-side normalization and planning only.
The canonical storage contract belongs in `ai-market-machine-data`.
Persistence remains deferred.
