# Market Calendar Consumer Readiness

This document defines how ingestion will consume the verified calendar read-only later.

## Consumer role

- ingestion will consume the calendar read-only
- ingestion has no schema ownership for calendar data
- the current minimal helper remains manual-only fallback

Mock expectations for the read-only consumer are documented in [Market Calendar Mock Consumer Contract](market_calendar_mock_consumer_contract.md).

## Shared use

The same consumer contract must serve:

- daily updates
- backfills
- flat-file coverage validation
- scheduler decisions
- gap-fill logic

## Ownership

`ai-market-machine-data` owns the persisted calendar schema.

## Safety

This consumer planning does not:

- call external services
- write to the database
- enable the scheduler
- add API routes
- add AI, trading, risk, signal, regime, portfolio, strategy, or prediction logic

`ai-market-machine-data` remains the schema owner.
