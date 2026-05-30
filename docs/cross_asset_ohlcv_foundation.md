# Cross-Asset OHLCV Foundation

This document describes the dry-run foundation for the cross-asset OHLCV ingestion slice.
It is planning and documentation only.

## Scope

- cross-asset OHLCV only
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

The normalized cross-asset OHLCV record includes:

- `symbol`
- `asset_group`
- `market_date`
- `open`
- `high`
- `low`
- `close`
- `volume`
- `source`
- `vendor_symbol`
- `notes`

The normalized field set is aligned to the existing OHLCV contract with added planning metadata.

## Dry-Run Contract

The dry-run command uses the deterministic manual fixture by default.
It reports:

- `record_count`
- `normalized_count`
- `valid_count`
- `invalid_count`
- `asset_groups`
- `symbols`
- `no_vendor_calls=True`
- `no_db_reads=True`
- `no_db_writes=True`

Optional flags:

- `--symbol`
- `--asset-group`
- `--show-records`
- `--show-invalid`

## Boundary Statement

The ingestion repo owns producer-side normalization and planning only.
The canonical storage contract belongs in `ai-market-machine-data`.
The writer plan is documentation only and does not enable persistence.
No AI/trading/risk/signal/regime/portfolio logic belongs in this foundation.
