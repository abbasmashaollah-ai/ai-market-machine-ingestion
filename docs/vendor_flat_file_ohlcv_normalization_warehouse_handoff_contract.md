# Vendor Flat-File OHLCV Normalization and Warehouse Handoff Contract

## Purpose

- define normalization and warehouse handoff contract for parsed vendor flat-file OHLCV records
- bridge local parser output to certified canonical evidence
- preserve 3-system boundary

## Input Contract

Input comes from local parser output only:

- symbol
- observation_date
- open
- high
- low
- close
- volume
- vwap
- transactions
- adjusted
- vendor
- asset_class
- schema_version
- dataset_version
- source_file_sha256
- lineage_id
- manifest_path
- source_file_name
- validation_status
- certification_status

## Canonical Normalized OHLCV Contract

Normalized output should include:

- symbol
- observation_date
- open
- high
- low
- close
- volume
- vwap
- transactions
- adjusted
- vendor
- asset_class
- source_schema_version
- canonical_schema_version `canonical_ohlcv.v1`
- dataset_version
- source_file_sha256
- lineage_id
- manifest_path
- source_file_name
- validation_status
- certification_status
- evidence_type `vendor_flat_file_ohlcv`
- evidence_type vendor_flat_file_ohlcv
- created_at
- idempotency_key

## Certification/Handoff Rules

- parser output with `FIXTURE_ONLY` remains fixture-only and must not be written as production evidence
- FIXTURE_ONLY remains fixture-only
- production certification requires validation_status PASS
- production certification requires checksum verified
- production certification requires no blocking validation errors
- production certification converts only approved records to CERTIFIED
- no checksum, no certification
- failed validation blocks warehouse handoff

## Idempotency Contract

- idempotency_key should be deterministic from vendor, asset_class, symbol, observation_date, dataset_version, source_file_sha256
- duplicate idempotency key should become IDEMPOTENT_NOOP or conflict depending on payload equality
- full idempotency key should not be printed in logs; use prefix only

## Warehouse Handoff Boundary

- ingestion prepares certified normalized evidence
- ai-market-machine-data owns canonical warehouse storage/read APIs
- handoff payload must be safe for data repo ingestion/storage
- AI Machine never consumes handoff files directly
- AI Machine consumes only certified Data API/evidence

## Replay/Backtest Boundary

- replay/backtest should use certified canonical OHLCV evidence
- historical run metadata must preserve manifest/checksum/lineage references
- parser fixture output alone is not enough for production replay

## Error Model

- HANDOFF_BLOCKED_FIXTURE_ONLY
- HANDOFF_BLOCKED_VALIDATION_FAILED
- HANDOFF_BLOCKED_CHECKSUM_MISSING
- HANDOFF_BLOCKED_CERTIFICATION_MISSING
- IDEMPOTENCY_CONFLICT
- IDEMPOTENT_NOOP

## Future Implementation Notes

- next implementation should be a pure local normalizer/handoff builder with tests
- no downloader
- no vendor activation
- no DB writes
- no scheduler
- no AI Machine runtime wiring

## Safety Confirmations

- no vendor calls
- no downloads
- no DB writes
- no ingestion run
- no scheduler activation
- no production changes
- no AI Machine runtime wiring
- no secrets committed
