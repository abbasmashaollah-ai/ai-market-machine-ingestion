# Sector ETF OHLCV Handoff Contract

## Purpose

- define the controlled handoff boundary for sector ETF OHLCV records
- keep ingestion responsible for producer-side shaping only
- keep ai-market-machine-data responsible for warehouse storage, certification, and reads

## Sector ETF Universe

The controlled sector ETF universe is:

- SPY
- XLB
- XLE
- XLF
- XLI
- XLK
- XLP
- XLRE
- XLU
- XLV
- XLY
- XLC

## Required Canonical Handoff Fields

A sector ETF OHLCV handoff record must include:

- symbol
- observation_date or timestamp
- open
- high
- low
- close
- volume
- timeframe
- adjusted
- source
- dataset_version
- schema_version
- validation_status
- certification_status
- lineage_id
- source_file_sha256 or equivalent source checksum
- deterministic idempotency key or uniqueness fields

## Allowed Statuses

- fixture-only records are not production eligible
- production-candidate records require an approved non-fixture source
- failed validation blocks handoff

## Boundary Rules

- ingestion produces handoff records only
- data accepts, stores, and certifies
- ingestion does not write production DB
- data does not call vendors to generate rows
- core does not consume raw handoff files

## Safety Rules

- no vendor calls
- no downloads
- no DB writes
- no scheduler activation
- no full secret or idempotency exposure
- no raw vendor data committed

## Next Implementation Step

The next implementation step after this contract is a pure local sector ETF OHLCV handoff dry-run using synthetic or approved local records only.

## Non-Goals

- no production write path
- no runtime writer logic
- no vendor activation
- no warehouse population
- no scheduler changes
