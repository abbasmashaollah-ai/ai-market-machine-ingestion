# Market Calendar Provider Comparison

This document compares the current minimal helper with the mock provider over a fixed date range.

## Purpose

- show behavior differences before any replacement or production calendar integration
- keep the comparison read-only
- never switch runtime behavior
- use exclusive end-date semantics so the reported range is deterministic

## Scope

- current minimal helper
- mock calendar provider
- exclusive end-date semantics in the diagnostic

## Safety

This comparison does not:

- call external services
- write to the database
- enable production behavior
- add API routes
- add AI, trading, risk, signal, regime, portfolio, strategy, or prediction logic

`ai-market-machine-data` remains the schema owner.

The next step is documented in [Verified Calendar Consumer Implementation Plan](verified_calendar_consumer_implementation_plan.md).
