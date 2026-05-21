# Normalization Layer

The normalization layer converts already-provided raw dictionaries into internal normalized dataclasses.

## Scope

This layer provides pure transformation helpers only:

- safe parsing helpers for text, booleans, numbers, decimals, dates, and timestamps
- UTC timestamp normalization
- OHLCV mapping from raw dictionaries to normalized internal records
- macro observation mapping from raw dictionaries to normalized internal records
- a placeholder boundary module for future corporate action work

## Boundary

This layer does not:

- call vendor APIs
- fetch data
- validate quality
- write to a database
- run pipelines
- run backfills
- start schedulers
- expose API routes
- perform AI or trading logic

## Design Notes

- The helpers are deterministic and side-effect free.
- Raw inputs are expected to be already available in memory as dictionaries.
- Configuration of key names is supported where it improves reuse without introducing vendor-specific logic.
