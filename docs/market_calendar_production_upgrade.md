# Market Calendar Production Upgrade

This document defines the requirements for moving from the current minimal calendar helper to a production-grade calendar.

The chosen provider strategy is documented in [Market Calendar Provider Strategy](market_calendar_provider_strategy.md). The hybrid approach is the selected direction.

## Current helper

The current helper remains safe for manual tests only. It is intentionally minimal and dependency-free.

## Production requirements

- holiday calendar support
- special market closures
- early closes
- timezone correctness
- exchange schedule determinism

## Shared use

The production calendar must be shared across:

- daily updates
- flat-file coverage validation
- scheduler decisions
- gap-fill logic

The production target must be deterministic and ultimately verified before use. The same verified calendar should be consumed consistently by ingestion, scheduler, and coverage checks.

## Safety

This upgrade planning does not:

- add trading or AI decision logic
- call external services
- write to the database
- add API routes
- enable the scheduler

`ai-market-machine-data` remains the schema owner.
