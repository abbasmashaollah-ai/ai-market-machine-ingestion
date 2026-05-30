# Fundamentals/Filings Foundation

This document describes the dry-run foundation for the fundamentals/filings ingestion slice.
It is planning and documentation only.

## Scope

- fundamentals/filings only
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

## Normalized Record Families

- `company_profile`
- `financial_statement`
- `financial_metric`
- `earnings_estimate`
- `sec_filing`

## Normalized Record Shape

The normalized fundamentals/filings record includes:

- `record_family`
- `symbol`
- `source`
- `record_date`
- `period`
- `payload`
- `notes`

The normalized field set is aligned to the planning contract for future data-side ownership.

## Dry-Run Contract

The dry-run command uses the deterministic manual fixture by default.
It reports:

- `record_count`
- `normalized_count`
- `valid_count`
- `invalid_count`
- `record_families`
- `symbols`
- `no_vendor_calls=True`
- `no_db_reads=True`
- `no_db_writes=True`

Optional flags:

- `--symbol`
- `--record-family`
- `--show-records`
- `--show-invalid`

## Boundary Statement

The ingestion repo owns producer-side normalization and planning only.
The canonical storage contract belongs in `ai-market-machine-data`.
The writer plan is documentation only and does not enable persistence.
No AI/trading/risk/signal/regime/portfolio logic belongs in this foundation.
