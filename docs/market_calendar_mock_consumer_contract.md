# Market Calendar Mock Consumer Contract

This document defines the mocked expectations for ingestion-side calendar consumption before DB integration exists.

## Contract expectations

- `is_trading_day` returns a bool
- `previous_trading_day` returns a date
- `next_trading_day` returns a date
- `trading_days` returns ordered dates
- `market_open_close` returns times
- `is_early_close` returns a bool
- `closure_reason` returns a nullable string

## Role

- ingestion consumes a read-only calendar contract
- ingestion does not own the calendar schema
- the current minimal helper remains manual-only fallback
- the same consumer must serve daily updates, backfills, flat-file coverage, scheduler, and gap-fill
- no trading or AI decision logic is introduced

The deterministic mock provider used by tests is documented in [Market Calendar Mock Provider](market_calendar_mock_provider.md).

## Safety

This mock contract planning does not:

- connect to a database
- write to the database
- call external services
- add API routes
- enable the scheduler

`ai-market-machine-data` remains the schema owner.
