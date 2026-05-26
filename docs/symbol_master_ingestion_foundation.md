# Symbol Master Ingestion Foundation

This document defines the ingestion-side dry-run foundation for symbol master work in `ai-market-machine-ingestion`.

## Scope

The foundation is intentionally read-only / dry-run only.

It may:

- normalize a small deterministic symbol fixture
- validate required symbol-master fields
- report input, normalized, valid, invalid, rows-written, rows-skipped, and confirmation counts
- write valid rows only when `--confirm-write` is explicitly requested through `app.writers.symbol_master_writer.SymbolMasterWriter`

It does not:

- call vendors
- write to the database
- own migrations
- own schema contracts
- add FastAPI routes
- add scheduler activation
- introduce AI/trading/risk/signal/regime/portfolio logic

## Record shape

The dry-run path uses `app.normalization.symbol_master.NormalizedSymbolMasterRecord` as the normalized output shape.

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
- `rows_written`
- `rows_skipped`
- `write_confirmed`
- `dry_run=true`

When `--confirm-write` is used, the command requires `DATABASE_URL`, uses `app.writers.symbol_master_writer.SymbolMasterWriter`, and still does not assume any scheduler ownership.

The confirmed-write path remains bounded to the approved writer/store boundary and does not create tables or run migrations.

`--record-run`, `--record-quality`, and `--record-lineage` are intentionally deferred until a symbol-master-specific evidence store contract is approved.

Preflight and evidence verification are available as read-only helpers:

- `scripts/preflight_symbol_master_operations.py`
- `scripts/verify_symbol_master_evidence_chain.py`

Reference docs:

- `docs/symbol_master_preflight.md`
- `docs/symbol_master_evidence_chain.md`

Those helpers stay read-only and do not introduce scheduler ownership or vendor dependencies.

## Boundary

The symbol master ingestion foundation stays on the producer side and is deliberately limited to dry-run and normalization behavior until a later write path is explicitly approved.

`ai-market-machine-data` remains the schema owner for the canonical symbol master contract.
