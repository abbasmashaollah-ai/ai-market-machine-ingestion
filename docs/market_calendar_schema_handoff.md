# Market Calendar Schema Handoff

This document defines the production calendar table/view/API contract that ingestion will consume later.

## Contract fields

- `exchange`
- `calendar_date`
- `is_trading_day`
- `open_time`
- `close_time`
- `is_early_close`
- `closure_reason`
- `source`
- `source_version`
- `generated_at`
- `verified_at`

## Ownership

`ai-market-machine-data` owns the table, view, or API schema.

## Ingestion role

- ingestion is a read-only consumer
- ingestion must not create or migrate calendar schema
- ingestion later consumes the verified calendar read-only
- the same verified calendar must drive daily updates, backfills, flat-file coverage, scheduler decisions, and gap-fill logic
- no trading or AI decision logic is introduced

## Safety

This handoff planning does not:

- connect to a database
- write to the database
- call external services
- add API routes
- enable the scheduler

`ai-market-machine-data` remains the schema owner.
