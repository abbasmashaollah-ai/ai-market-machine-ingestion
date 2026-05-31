# Options Foundation

This document describes the dry-run foundation for the options ingestion slice.
It is planning and documentation only.

## Scope

- options only
- dry-run and normalization only
- writer-readiness planning only
- no vendor calls
- no DB reads
- no DB writes
- no scheduler
- no FastAPI routes
- no migrations
- no schema ownership
- no AI/trading/risk/signal/regime/portfolio logic

## Normalized Record Shape

The normalized options record includes:

- `contract_symbol`
- `underlying_symbol`
- `expiration_date`
- `strike`
- `option_type`
- `bid`
- `ask`
- `last`
- `volume`
- `open_interest`
- `implied_volatility`
- `source`
- `notes`

The normalized field set is aligned to the planning contract for future data-side ownership.

## Dry-Run Contract

The dry-run command uses the deterministic manual fixture by default.
It reports:

- `record_count`
- `normalized_count`
- `valid_count`
- `invalid_count`
- `underlying_symbols`
- `option_types`
- `no_vendor_calls=True`
- `no_db_reads=True`
- `no_db_writes=True`

Optional flags:

- `--underlying-symbol`
- `--option-type`
- `--show-records`
- `--show-invalid`

## Boundary Statement

The ingestion repo owns producer-side normalization and planning only.
The canonical storage contract belongs in `ai-market-machine-data`.
The writer plan is documentation only and does not enable persistence.
No AI/trading/risk/signal/regime/portfolio logic belongs in this foundation.
