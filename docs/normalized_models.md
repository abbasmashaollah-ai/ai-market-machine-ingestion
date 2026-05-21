# Normalized Models

These models define the internal shape of records after vendor mapping and before quality validation or writing.

## Scope

The normalized model layer provides:

- `NormalizedOHLCVRecord`
- `NormalizedMacroObservation`
- `NormalizedSymbolRecord`
- vendor payload metadata

## Boundary

These are internal contracts only. They are not vendor clients, not validation pipelines, and not persistence models.

## Contract Notes

- `symbol` and `symbol_id` are optional because vendor source records may arrive before final canonical resolution.
- `timestamp` is normalized to UTC-aware datetime form.
- `market_date` is optional for date-aligned records.
- `timeframe` is required and defaults to a daily-style contract when not explicitly provided.
- `adjusted` is explicit and preserved.
- OHLCV fields are represented directly on the normalized record.
- Metadata fields such as `vendor`, `source`, `ingestion_run_id`, `normalization_version`, and `quality_status` travel with the record when available.

## Alignment With Data Contracts

These models are designed to align with the high-level approved table contracts in `docs/data_contracts.md`, especially the `canonical_ohlcv`, `symbol_master`, and operational lineage/quality expectations.
