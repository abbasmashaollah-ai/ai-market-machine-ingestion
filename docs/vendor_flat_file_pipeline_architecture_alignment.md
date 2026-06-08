# Vendor Flat-File Pipeline Architecture Alignment

## Purpose

- lock the vendor flat-file pipeline architecture
- prevent per-feature vendor downloaders
- preserve the 3-system boundary before more implementation

## Correct Flow

- vendor adapter downloads/acquires once
- raw file is stored/stamped
- manifest/checksum verifies what arrived
- normalizer converts to canonical records
- validator checks quality
- evidence/certification records why data is trusted
- feature builders consume canonical/certified data
- ai-market-machine-data owns canonical warehouse/read APIs
- AI Machine consumes certified Data API/evidence only

## Explicit Anti-Pattern

- `features/prices/download_polygon_flat_files.py`
- `features/breadth/download_polygon_flat_files.py`
- `features/options/download_polygon_flat_files.py`
- `features/earnings/download_polygon_flat_files.py`

Why these are bad:

- duplicate downloads
- duplicate vendor logic
- duplicate checkpoints
- inconsistent validation
- inconsistent lineage
- harder debugging

## Preferred Folder Responsibility

- `app/vendors/polygon/api/`
- `app/vendors/polygon/flat_files/`
- `app/raw_store/`
- `app/normalization/ohlcv/`
- `app/normalization/options/`
- `app/validation/ohlcv/`
- `app/validation/options/`
- `app/evidence/`
- `app/features/prices/`
- `app/features/breadth/`
- `app/features/options/`
- `app/features/macro/`
- `app/writers/`

## Feature Folder Rule

Feature folders are vendor-agnostic.

Examples:

- `features/prices` consumes `CanonicalDailyBar`, adjusted OHLCV, symbol master
- `features/breadth` consumes canonical OHLCV universe and universe snapshots
- `features/options` consumes canonical options chain/snapshot data
- `features/macro` consumes canonical macro observations
- `features/market_bundle` consumes certified feature/evidence outputs

## Current Implementation Position

- `app/vendor_flat_files/local_ohlcv_parser.py` exists as a local-file-only parser
- it is acceptable as the first small local parser
- future refinement may split responsibilities into:
  - `app/vendors/polygon/flat_files/local_reader.py`
  - `app/normalization/ohlcv/polygon_flat_file_normalizer.py`
  - `app/validation/ohlcv/daily_bar_validator.py`
- do not refactor yet without a separate review

## Next Recommended Step

- create a normalization/warehouse handoff contract
- still no downloader
- still no vendor activation
- still no DB writes
- still no AI Machine runtime wiring

## Safety Confirmations

- no vendor calls
- no downloads
- no DB writes
- no ingestion run
- no scheduler activation
- no production changes
- no AI Machine runtime wiring
- no secrets committed
