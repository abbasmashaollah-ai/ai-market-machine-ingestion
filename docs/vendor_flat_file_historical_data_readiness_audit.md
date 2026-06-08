# Vendor Flat-File Historical Data Readiness Audit

## Purpose

- perform a system review and gap analysis for vendor flat-file historical data readiness
- preserve the 3-system boundary before any implementation work

## Current Readiness Status

- `ai-market-machine-ingestion` is the producer/workflow repo
- `ai-market-machine-data` is the data-service/warehouse repo
- `ai-market-machine-core` is the AI reasoning system
- ai-market-machine-ingestion is the producer/workflow repo
- ai-market-machine-data is the data-service/warehouse repo
- ai-market-machine-core is the AI reasoning system
- stocks/equities
- the repo is not ready for vendor flat-file historical data work as a production implementation
- what already exists is planning, boundary definition, and some vendor/source foundations
- what is missing is a production runtime flat-file adapter, local flat-file reader, manifest/checksum layer, and certified warehouse handoff
- no paid vendor activation
- no large downloads
- what should not be built yet is paid vendor activation, large downloads, or AI Machine consumption of raw vendor files
- the safest next single step is docs/contracts plus fixture samples for the flat-file path

## Existing Implementation Inventory

- vendor adapters: present
- Polygon API adapter: present
- Polygon flat-file adapter: missing in runtime code
- local flat-file reader: missing
- download client: planning-only surfaces present
- manifest schema: planning-only
- checksum validator: planning-only
- compression handling: not proven as a flat-file runtime path
- file layout conventions: planning-only
- OHLCV normalization: present
- options chain normalization: partial/planning-only
- futures normalization: partial/planning-only
- indices/ETF support: partial, mostly through vendor/source foundations and planning docs
- symbol master/reference support: present
- corporate actions support: partial/planning-only
- validation gates: present
- lineage/evidence model: present
- certification gates: present
- warehouse handoff: present as guarded writer boundary, not yet a flat-file handoff contract
- replay/backtest support: partial/planning-only
- scheduler/daily job surfaces: present in planning and some runtime work, but not flat-file ready
- tests and fixtures: present for planning and related Polygon/OHLCV slices

## Target Architecture Recommendation

- vendor raw landing area
- normalized staging area
- certified evidence output
- manifest/checksum layer
- validation/certification layer
- lineage layer
- warehouse handoff to `ai-market-machine-data`
- AI Machine consumption only through certified Data API/evidence

## Asset-Class Sequencing

Recommended order:

1. equities/daily OHLCV first
2. ETFs/daily OHLCV
3. indices/daily OHLCV
4. symbol master/corporate actions
5. options EOD chains
6. futures EOD
7. macro/rates/news/dark pool later

## Flat-File Layout Proposal

- `data/vendor/polygon/flatfiles/equities/daily/YYYY/MM/DD/`
- `data/vendor/polygon/flatfiles/etfs/daily/YYYY/MM/DD/`
- `data/vendor/polygon/flatfiles/indices/daily/YYYY/MM/DD/`
- `data/vendor/polygon/flatfiles/options/daily/YYYY/MM/DD/`
- `data/vendor/polygon/flatfiles/futures/daily/YYYY/MM/DD/`
- manifests next to raw files
- checksums next to raw files
- no raw vendor data committed to git

## Risk Classification

- vendor cost/activation risk: HIGH
- large file/storage risk: HIGH
- duplicate download risk: MEDIUM
- bad checksum risk: HIGH
- schema drift risk: HIGH
- options data volume risk: HIGH
- futures symbology risk: MEDIUM
- corporate actions adjustment risk: HIGH
- scheduler risk: HIGH
- production DB write risk: HIGH
- AI Machine contamination risk: HIGH
- secrets exposure risk: HIGH

## Required Steps Before Real Vendor Activation

1. docs/contracts
2. fixture samples
3. manifest schema
4. checksum validation
5. local parser
6. normalization contract
7. validation tests
8. lineage evidence
9. warehouse handoff contract
10. replay/backtest contract
11. small approved pilot
12. only then vendor activation/downloads

## Go/No-Go Conclusion

- GO_NOW is not appropriate
- NO_GO for implementation now
- status: `GO_AFTER_CONTRACTS`
- recommended next single step: write the docs/contracts and fixture samples that define the flat-file contract before any runtime build

## Safety Confirmations

- no vendor calls
- no downloads
- no DB writes
- no ingestion run
- no scheduler activation
- no production changes
- no AI Machine runtime wiring
- no secrets committed
