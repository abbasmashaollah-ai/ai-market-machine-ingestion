# Polygon Flat-File Quarantine Policy

This document defines how invalid flat files are isolated before any parse or persistence step.

## Policy

- quarantine is mandatory for failed integrity and parse cases
- quarantined files are excluded from parsing and persistence
- replay or retry from quarantine requires manual review
- manifest must record quarantine status and reason
- this policy remains planning-only until file operations exist

## Reason codes

- `checksum_failed`
- `size_check_failed`
- `empty_file`
- `schema_probe_failed`
- `parse_failed`
- `manual_review`

## Safety

This policy does not:

- call Polygon
- call S3
- download files
- write files
- write to the database
- add scheduler behavior
- add API routes
- add AI, trading, risk, signal, regime, portfolio, strategy, or prediction logic

`ai-market-machine-data` remains the schema owner.
