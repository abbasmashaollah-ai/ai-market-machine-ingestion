# Sector Rotation Certified OHLCV Live Read Plan

## Purpose

This plan defines the live read-only verification flow for the sector rotation certified OHLCV adapter.

The adapter already exists in mocked/test-only form. This document describes the additional live read verification required before any production-adjacent use.

## Current Adapter Status

- the sector rotation adapter exists in `app/features/sector_rotation/sector_rotation_reader.py`
- it uses `DataReadClient`
- it is covered by mocked unit tests only
- live endpoint verification has not been done

## Required Sector Symbols

- `SPY`
- `XLC`
- `XLY`
- `XLP`
- `XLE`
- `XLF`
- `XLV`
- `XLI`
- `XLB`
- `XLRE`
- `XLK`
- `XLU`

## Minimum Lookback

The live read should supply enough history for 60d returns.

Practical minimum: at least 61 trading rows per required symbol.

## Live Verification Flow

1. verify the OpenAPI route exists
2. call the certified OHLCV read endpoint once per required symbol
3. confirm response rows contain `symbol`, `date` or `timestamp`, and `close`
4. pass the combined `historical_ohlcv` rows to `build_price_history_by_symbol(...)`
5. run `run_sector_rotation_certified_ohlcv_dry_run(...)` in read-only mode
6. confirm 11 observation rows and 1 summary row

## Expected Warnings

The live path may warn on:

- missing symbols
- insufficient history
- stale rows
- uncertified rows

The live response shape should use `historical_ohlcv` for each symbol response.

## Safety Boundaries

- no real writer
- no DB writes
- no vendor calls
- no scheduler activation
- no AI Machine changes
- no token logging

## Approval Gate Before Any Live Read Command

Human approval is required before executing any live read command against `ai-market-machine-data`.

This is a verification plan only and does not authorize execution.

Human approval must happen before any live sector rotation verification step is executed.

human approval

The manual SPY live read returned `200`, confirming the route shape and read-only access, but this plan still requires human approval before any additional live calls.
