# Multi-Symbol FMP OHLCV Fan-Out

This document covers the controlled fan-out layer that reuses the existing single-symbol FMP OHLCV ingestion orchestrator.

## Behavior

The fan-out layer:

- accepts an ordered list of symbols
- accepts the same requested start and end dates as the single-symbol slice
- calls the existing single-symbol orchestrator once per symbol
- aggregates the per-symbol plans into a deterministic batch result
- preserves the ingestion-only boundary

The batch result includes:

- `requested_symbols`
- `completed_symbols`
- `failed_symbols`
- `per_symbol_results`
- aggregate raw and normalized counts
- aggregate writer and checkpoint status
- `batch_errors`
- `did_write_db`

## Default mode

Default execution is still dry-run/write-plan only.

That means:

- no writer execution by default
- no checkpoint persistence by default
- `did_write_db: false` unless a caller explicitly enables writer execution and a symbol plan reports success

## Failure handling

By default, one symbol failure does not stop the remaining symbols.

Each symbol is isolated behind the single-symbol orchestrator result. The fan-out layer records failures in the batch output and keeps going unless the caller enables `fail_fast`.

## Fail-fast mode

`fail_fast` defaults to `false`.

When `fail_fast: true`:

- the fan-out stops after the first symbol failure
- later symbols are not processed

## Writer and checkpoint pass-through

Writer and checkpoint objects are only forwarded to the single-symbol orchestrator when the caller explicitly requests execution.

That keeps the default batch path dry-run only and avoids accidental live persistence.

## Why scheduler and cron remain disabled

This layer is an ingestion primitive, not an execution schedule.

Scheduler and cron wiring stay out of scope so the repository can prove the batch plan shape first without creating a live recurring job surface.

## Remaining work before the data repo can facade or delete old OHLCV modules

Before `ai-market-machine-data` can facade or remove its remaining OHLCV ingestion modules, the data-side callers still need to switch over to this ingestion-owned fan-out path and any remaining runtime entry points need to be updated to use the new batch result contract.
