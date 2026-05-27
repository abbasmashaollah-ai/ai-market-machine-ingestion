# Earnings Calendar Foundation

This document describes the fixture-backed earnings calendar foundation.
It is documentation and dry-run planning only.

## Scope

- earnings calendar only
- fixture-backed dry-run planning only
- no vendor calls
- no DB reads
- no DB writes
- no scheduler
- no FastAPI routes
- no migrations
- no schema ownership
- no AI/trading/risk/signal/regime/portfolio logic

## Fixture Records

The deterministic fixture set includes earnings-date records with:

- `event_type=earnings_date`
- `source=manual_fixture`
- `symbol`
- `event_date`
- `event_time` nullable
- `timezone` explicit when `event_time` exists
- `title`
- `importance`
- `notes`
- stable `event_id` values like `EARNINGS-SYMBOL-YYYY-MM-DD`

## Dry-Run Contract

The dry-run command reports:

- `event_count`
- `normalized_count`
- `valid_count`
- `invalid_count`
- `symbols`
- `no_vendor_calls=True`
- `no_db_reads=True`
- `no_db_writes=True`

Optional flags:

- `--symbol`
- `--show-events`
- `--show-invalid`

## Boundary

No persistence is allowed until the data-side table and writer boundary are approved.
No vendor calls, DB reads, DB writes, scheduler behavior, FastAPI routes, migrations, schema ownership, AI, trading, risk, signal, regime, or portfolio logic belong here.

