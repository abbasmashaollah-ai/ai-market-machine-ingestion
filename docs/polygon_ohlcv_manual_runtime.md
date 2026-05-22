# Manual Polygon OHLCV Runtime

This repository now provides a manual Polygon OHLCV runtime built with the same operator safety model as the manual FRED macro path.

## Scope

The runtime is manual-only and provides:

- dry-run fetch/normalize/validate for a small symbol set
- confirmed persistence through the approved OHLCV writer
- checkpoint-based resume behavior through `ingestion_checkpoints`
- checkpoint inspection for manual verification
- per-symbol summaries and aggregate summaries
- live HTTP transport wiring through the shared standard-library client when `POLYGON_API_KEY` is present

## Safety

The runtime does not:

- run automatically on Railway startup
- start a scheduler
- expose API routes
- run migrations
- create tables
- add schema ownership here
- print `POLYGON_API_KEY`
- print `DATABASE_URL`

`ai-market-machine-data` remains the schema owner.

## Approved Output

The approved target table is `canonical_ohlcv`, as documented in `docs/data_contracts.md`.

The approved writer boundary lives in `app/writers/ohlcv_writer.py`.

## Verification Log

- Successful live persistence and checkpoint verification were completed for `SPY` over `2025-01-02` to `2025-01-10`
- `canonical_ohlcv` sequence drift was repaired in `ai-market-machine-data` before the successful run
