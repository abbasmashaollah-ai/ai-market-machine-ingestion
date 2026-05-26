# Volatility Index Foundation

This document describes the dry-run foundation for the `volatility_index` ingestion slice.
It is planning and documentation only.

## Scope

- volatility indexes only
- dry-run and normalization only
- no DB writes
- no vendor calls by default
- no scheduler
- no FastAPI routes
- no migrations
- no schema ownership
- no AI/trading/risk/signal/regime/portfolio logic

## Starter Symbols

- `VIX`
- `VVIX`
- `VXN`
- `RVX`

## Normalized Record Shape

The normalized volatility index record includes:

- `symbol`
- `observation_date`
- `value`
- `source`
- `vendor_symbol`
- `unit`
- `notes`

## Dry-Run Contract

The dry-run command uses the deterministic sample fixture by default.
It reports:

- `symbol_count`
- `normalized_count`
- `valid_count`
- `invalid_count`
- `starter_symbols`
- `no_vendor_calls=true`
- `no_db_writes=true`

Optional flags:

- `--show-symbols`
- `--show-invalid`

## Boundary Statement

The ingestion repo owns producer-side normalization and planning only.
The canonical storage contract belongs in `ai-market-machine-data`.
No AI/trading/risk/signal/regime/portfolio logic belongs in this foundation.
