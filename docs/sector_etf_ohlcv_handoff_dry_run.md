# Sector ETF OHLCV Handoff Dry Run

## Purpose

- prove ingestion can build safe handoff records for the controlled 12-symbol sector ETF universe
- keep the dry run local, deterministic, and non-production

## Universe

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

## Dry-Run Behavior

- uses synthetic or approved local records only
- feeds the existing local parser and OHLCV handoff builder
- prints a safe summary only
- never writes to DB
- never calls vendors
- never downloads files
- never activates schedulers
- never prints full idempotency keys

## Safe Summary Fields

- universe_count
- records_generated
- symbols_ready
- symbols_missing
- validation_status
- certification_status
- production_eligible
- fixture_only
- db_write_attempted
- vendor_call_attempted
- download_attempted
- scheduler_activation_attempted
- idempotency_key_prefixes

## Expected Result

- all 12 sector ETF symbols are ready
- no symbols are missing
- validation status is PASS
- certification status remains FIXTURE_ONLY
- production eligibility is false

## Boundary

- ingestion produces handoff records only
- data accepts, stores, and certifies
- core does not consume raw handoff files

## Next Step

- follow this dry run with an approved ingestion-to-data transfer path once the data repo confirms warehouse acceptance
