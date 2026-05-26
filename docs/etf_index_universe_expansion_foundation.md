# ETF/Index Universe Expansion Foundation

This document defines the dry-run planning foundation for ETF/index universe expansion.

## Scope

The foundation is intentionally read-only.

It may:

- build deterministic ETF/index candidate groups
- describe core ETF, sector ETF, and major index proxy coverage
- optionally compare candidate symbols against `public.symbol_master` when explicitly requested
- report candidate counts, found counts, missing counts, and group counts
- support targeted live lookup through `scripts/fetch_polygon_symbol_master_by_symbols.py`

## Index labels versus proxies

Major index coverage is modeled as index labels with tradable ETF proxies:

- SPX maps to SPY
- NDX maps to QQQ
- RUT maps to IWM
- DJI maps to DIA

The index label is tracked as planning context, while the proxy symbol is what the dry-run check expects in `public.symbol_master`.
The major-index candidate records carry `index_symbol` for the label and `proxy_symbol` for the tradable ETF, with `active_required=false` on the label and `proxy_required=true` on the proxy.

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
`scripts/fetch_polygon_symbol_master_by_symbols.py` is the manual targeted lookup command.

It prints:

- `candidate_count`
- `found_count`
- `missing_count`
- `group_counts`
- `no_vendor_calls=true`
- `no_db_writes=true`
- `--show-missing` prints `missing_symbols`
- `--show-found` prints `found_symbols`

When `--check-symbol-master` is used, the command requires `DATABASE_URL` and reads `public.symbol_master` only.
When `--live-check` is used on the targeted lookup command, `POLYGON_API_KEY` is required and `SymbolMasterWriter` remains the only persistence path when `--confirm-write` is also set.

## Boundary

The ETF/index universe foundation depends on symbol-master records and stays on the producer/planning side until a later verified write path is explicitly approved.
