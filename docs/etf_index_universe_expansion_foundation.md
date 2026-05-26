# ETF/Index Universe Expansion Foundation

This document defines the dry-run planning foundation for ETF/index universe expansion.

## Scope

The foundation is intentionally read-only.

It may:

- build deterministic ETF/index candidate groups
- describe core ETF, sector ETF, and major index proxy coverage
- optionally compare candidate symbols against `public.symbol_master` when explicitly requested
- report candidate counts, found counts, missing counts, and group counts

It does not:

- call vendors by default
- write to the database
- own migrations
- own schema contracts
- add FastAPI routes
- add scheduler activation
- introduce AI/trading/risk/signal/regime/portfolio logic

## Candidate groups

- core ETFs
- sector ETFs
- major index proxies
- planned industry ETF placeholders

## Manual command

`scripts/dry_run_etf_index_universe_expansion.py` is the operator-facing dry-run command.

It prints:

- `candidate_count`
- `found_count`
- `missing_count`
- `group_counts`
- `no_vendor_calls=true`
- `no_db_writes=true`

When `--check-symbol-master` is used, the command requires `DATABASE_URL` and reads `public.symbol_master` only.

## Boundary

The ETF/index universe foundation depends on symbol-master records and stays on the producer/planning side until a later verified write path is explicitly approved.
