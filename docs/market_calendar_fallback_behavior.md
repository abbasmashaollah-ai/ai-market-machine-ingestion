# Market Calendar Fallback Behavior

This document defines when the current minimal helper may be used and when it may not.

## Allowed fallback use

- manual tests
- planning diagnostics

## Forbidden fallback use

- production scheduler
- large backfills
- flat-file persistence
- official gap-fill decisions

## Current state

- the minimal helper remains manual-only
- the production calendar must be verified before automation or scale

## Shared use

The verified production calendar must ultimately drive:

- daily updates
- backfills
- flat-file coverage
- scheduler decisions
- gap-fill logic

## Safety

This fallback planning does not:

- add trading or AI decision logic
- call external services
- write to the database
- add API routes
- enable the scheduler

`ai-market-machine-data` remains the schema owner.
