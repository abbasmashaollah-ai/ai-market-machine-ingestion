# Vendor Flat-File OHLCV Handoff Builder Implementation

## Purpose

- implement a pure local normalizer/handoff builder
- convert parsed local parser output into canonical normalized OHLCV handoff records

## Implementation Summary

- pure local normalizer/handoff builder exists
- parsed local parser output only
- canonical_schema_version `canonical_ohlcv.v1`
- evidence_type `vendor_flat_file_ohlcv`
- `FIXTURE_ONLY` remains blocked from production warehouse handoff
- fixture_only remains blocked from production warehouse handoff
- parser fixture output is not production evidence
- no warehouse writer
- no downloader
- no vendor calls
- no downloads
- no DB writes
- no scheduler activation
- no AI Machine runtime wiring

## Handoff Rules

- idempotency key is deterministic
- safe summary exposes idempotency key prefix only
- prefix-only safe summary
- full idempotency key stays internal to the handoff record
- replay/backtest uses certified canonical OHLCV evidence later
- warehouse writer comes later after separate approval

## Safety Notes

- local function style
- no env vars read
- no requests/http/vendor SDK imports
- no DB or writer imports
- no output files written
