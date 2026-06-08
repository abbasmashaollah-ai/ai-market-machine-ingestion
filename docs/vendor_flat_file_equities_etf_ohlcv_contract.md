# Vendor Flat-File Equities ETF OHLCV Contract

## Purpose

- define the first vendor flat-file contract for equities and ETFs daily OHLCV
- prepare historical backtest/replay support without vendor activation
- preserve the 3-system boundary

## Scope

- asset class: equities and ETFs
- first vendor model: Polygon-style flat files
- data type: daily OHLCV
- intended future symbols: SPY, QQQ, IWM, DIA, XLC, XLY, XLP, XLE, XLF, XLV, XLI, XLB, XLRE, XLK, XLU
- no options/futures implementation yet
- no paid vendor activation
- no large downloads

## Proposed Raw Flat-File Layout

- `data/vendor/polygon/flatfiles/equities/daily/YYYY/MM/DD/`
- `data/vendor/polygon/flatfiles/etfs/daily/YYYY/MM/DD/`
- `manifest.json` next to raw files
- checksums next to raw files
- no raw vendor data committed to git

## Manifest Contract

Manifest fields:

- vendor
- asset_class
- data_type
- date
- schema_version
- dataset_version
- source_file_name
- source_file_size_bytes
- source_file_sha256
- compression
- row_count
- symbols_count
- created_at
- download_mode
- validation_status
- validation_errors
- lineage_id
- certification_status

## Checksum Contract

- SHA256 required
- checksum must be calculated before parsing
- checksum must be verified before normalization
- checksum mismatch blocks certification
- duplicate file detection uses vendor/date/asset_class/hash
- no checksum, no certification

## Raw File Contract

Expected columns:

- ticker
- date
- open
- high
- low
- close
- volume
- vwap if available
- transactions if available
- adjusted flag if available

## Normalized OHLCV Contract

Normalized fields:

- symbol
- observation_date
- open
- high
- low
- close
- volume
- vwap
- transactions
- vendor
- asset_class
- source_file_sha256
- lineage_id
- validation_status
- certification_status

## Validation Rules

- reject missing symbol
- reject missing date
- reject invalid OHLC values
- reject negative volume
- reject duplicate symbol/date rows
- reject checksum mismatch
- warn on missing optional vwap/transactions
- block certification on validation failure

## Warehouse Handoff

- ingestion prepares certified normalized evidence
- ai-market-machine-data owns canonical warehouse storage/read APIs
- ai-market-machine-data owns canonical warehouse storage/read APIs
- AI Machine consumes only certified Data API/evidence
- no AI Machine raw vendor file consumption

## Replay/Backtest Usage

- flat-file history should support deterministic backtests
- replay should read certified normalized evidence, not raw vendor files
- historical runs must record manifest/checksum/lineage references

## Future Extension Notes

- options EOD chain contract later
- futures EOD contract later
- index OHLCV contract later
- corporate actions adjustment contract later
- daily download scheduler only after contracts/fixtures/parser/validation are complete

## Safety Confirmations

- no vendor calls
- no downloads
- no DB writes
- no ingestion run
- no scheduler activation
- no production changes
- no AI Machine runtime wiring
- no secrets committed
