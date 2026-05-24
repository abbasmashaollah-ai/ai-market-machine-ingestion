# Market Calendar Provider Interface

This document defines the read-only interface that ingestion will consume later.

## Interface contract

- `is_trading_day(date)`
- `previous_trading_day(date)`
- `next_trading_day(date)`
- `trading_days(start_date, end_date)`
- `market_open_close(date)`
- `is_early_close(date)`
- `closure_reason(date)`

## Role

- ingestion consumes a read-only verified calendar interface later
- `ai-market-machine-data` owns the persisted calendar schema
- the same interface must be used by daily update, backfill, flat-file coverage, scheduler, and gap-fill
- the current minimal helper remains manual-only fallback
- no trading or AI decision logic is introduced

Fallback behavior is documented in [Market Calendar Fallback Behavior](market_calendar_fallback_behavior.md). The minimal helper is allowed only for manual tests and planning diagnostics.

## Safety

This interface planning does not:

- call external services
- write to the database
- enable the scheduler
- add API routes
- add AI, trading, risk, signal, regime, portfolio, strategy, or prediction logic

`ai-market-machine-data` remains the schema owner.
