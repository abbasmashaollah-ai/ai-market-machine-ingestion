# Vendor Flat-File Equities ETF OHLCV Local Parser Contract

## Purpose

- define local parser contract for synthetic Polygon-style equities/ETF daily OHLCV fixtures
- prepare parser implementation without vendor activation or runtime downloader
- preserve 3-system boundary

## Inputs

- CSV fixture path
- manifest path next to raw CSV
- asset_class equities or etfs
- observation_date
- expected schema_version `vendor_flat_file_ohlcv.v1`
- expected dataset_version `fixture.v1` for fixtures
- no remote URLs
- no vendor credentials

## Required Pre-Parse Checks

- manifest exists
- CSV exists
- source_file_sha256 matches actual CSV
- SHA256 verified before parsing
- manifest date matches path/date
- asset_class matches expected path
- validation_status PASS
- certification_status FIXTURE_ONLY for fixtures
- no checksum, no parse
- no checksum, no certification

## Raw Parse Contract

- parse required columns: ticker, date, open, high, low, close, volume
- parse optional columns: vwap, transactions, adjusted
- preserve original ticker casing normalized to uppercase symbol
- parse dates as ISO YYYY-MM-DD
- parse numeric fields deterministically
- reject malformed rows
- do not infer missing required values

## Normalized Output Contract

Each parsed row should produce:

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
- vendor polygon
- asset_class
- schema_version `vendor_flat_file_ohlcv.v1`
- dataset_version `fixture.v1`
- source_file_sha256
- lineage_id
- manifest_path
- source_file_name
- validation_status
- certification_status `FIXTURE_ONLY` for fixture parser output

## Validation Behavior

- reject missing ticker
- reject missing date
- reject open/high/low/close <= 0
- reject high less than low
- reject negative volume
- reject duplicate symbol/date
- warn but allow missing optional vwap
- warn but allow missing optional transactions
- block normalization on checksum mismatch
- block certification on validation failure

## Error Model

Structured errors:

- MANIFEST_MISSING
- CSV_MISSING
- CHECKSUM_MISMATCH
- REQUIRED_COLUMN_MISSING
- REQUIRED_VALUE_MISSING
- INVALID_OHLC
- NEGATIVE_VOLUME
- DUPLICATE_SYMBOL_DATE
- SCHEMA_VERSION_MISMATCH
- ASSET_CLASS_MISMATCH

## Safety

- local files only
- no vendor calls
- no downloads
- no DB writes
- no scheduler activation
- no AI Machine runtime wiring
- no secrets/tokens/raw provider credentials

## Future Parser Implementation Notes

- parser should be pure function style where possible
- tests should use only synthetic fixtures
- runtime downloader comes later
- warehouse handoff comes after parser + normalization validation
- AI Machine consumes only certified Data API/evidence, not parser output directly
