# Sector ETF OHLCV Production Handoff Provenance

## Purpose

Define the provenance and approval boundary for production sector ETF OHLCV handoff generation in `ai-market-machine-ingestion`.

## Production provenance requirement

Production sector ETF OHLCV handoff records must come from approved vendor-produced records only.

## Forbidden production inputs

The following are forbidden for production handoff generation:

- synthetic fixtures
- dry-run artifacts
- fixture-only records
- local test fixtures

## Sector universe

The sector ETF universe includes SPY as the benchmark and the 11 sector ETFs missing from production canonical OHLCV coverage:

- SPY
- XLB
- XLC
- XLE
- XLF
- XLI
- XLK
- XLP
- XLRE
- XLU
- XLV
- XLY

## Required production handoff fields

Production handoff records must include:

- symbol
- observation_date or timestamp
- open
- high
- low
- close
- volume
- timeframe
- adjusted
- source or vendor
- dataset_version
- schema_version
- validation_status
- certification_status
- lineage_id
- checksum or source_file_sha256
- deterministic idempotency_key

## Production eligibility requirements

Production-eligible records must have:

- validation_status = PASS
- certification_status not equal to FIXTURE_ONLY
- approved vendor/source attribution
- lineage preserved
- checksum preserved

## Approval boundary

Production handoff generation must require the production-specific approval phrase:

`APPROVE SECTOR ETF OHLCV PRODUCTION HANDOFF GENERATION`

The sector rotation production activation phrase must not be reused as the ingestion handoff phrase.

The test-db approval phrase must not be accepted.

## Authorization boundary

This docs-only step does not authorize:

- vendor calls
- downloads
- exports
- live ingestion
- scheduler activation
- DB writes
- production mutation

## Repo boundary

- ingestion produces approved vendor handoff records
- data repo accepts, stores, and certifies
- core interprets deterministic evidence

## Next allowed implementation step

The next allowed implementation after this docs/tests step should be a read-only vendor connectivity/provenance preflight, not production export.
