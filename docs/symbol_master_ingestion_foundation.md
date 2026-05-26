# Symbol Master Ingestion Foundation

This document defines the ingestion-side dry-run foundation for symbol master work in `ai-market-machine-ingestion`.

## Scope

The foundation is intentionally read-only / dry-run only.

It may:

- normalize a small deterministic symbol fixture
- validate required symbol-master fields
- report input, normalized, valid, and invalid counts

It does not:

- call vendors
- write to the database
- own migrations
- own schema contracts
- add FastAPI routes
- add scheduler activation
- introduce AI/trading/risk/signal/regime/portfolio logic

## Record shape

The dry-run path uses `app.normalization.symbol_master.NormalizedSymbolRecord` as the normalized output shape.

## Validation

The foundation validates:

- `symbol` is required
- `active` is required
- `vendor` and `vendor_symbol` are consistent when present
- `asset_type` is optional but normalized
- `exchange` is optional but normalized

## Manual command

`scripts/dry_run_symbol_master_ingestion.py` is the operator-facing dry-run command.

It prints:

- `input_count`
- `normalized_count`
- `valid_count`
- `invalid_count`
- `dry_run=true`

## Boundary

The symbol master ingestion foundation stays on the producer side and is deliberately limited to dry-run and normalization behavior until a later write path is explicitly approved.

`ai-market-machine-data` remains the schema owner for the canonical symbol master contract.
