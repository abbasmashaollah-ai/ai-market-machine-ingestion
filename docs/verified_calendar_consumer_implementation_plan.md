# Verified Calendar Consumer Implementation Plan

This document defines the next step after the mock-vs-minimal comparison: a verified calendar consumer path for ingestion.

## Direction

- the minimal helper must not be expanded blindly into production behavior
- the verified calendar consumer is the production path
- `ai-market-machine-data` owns the persisted calendar
- ingestion consumes that calendar read-only

## Shared use

The same verified calendar must drive:

- daily updates
- backfills
- flat-file coverage
- scheduler decisions
- gap-fill logic

## Known comparison gap

The current minimal helper misses at least the `2025-01-01` closure that appears in the mock fixture comparison.

## Safety

This plan does not:

- call external services
- read or write the database
- add schema changes or migrations
- add API routes
- enable the scheduler
- add trading or AI decision logic

