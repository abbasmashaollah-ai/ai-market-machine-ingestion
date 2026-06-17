# Polygon Stock Day Agg Warehouse Handoff Candidate Preview

This script is for local warehouse handoff candidate preview only.

It reads a downloaded Polygon stock day aggregates gzip CSV from disk, reuses the local normalization preview, and maps those normalized rows into an in-memory handoff candidate shape.

It does not:

- call vendor APIs
- download remote files
- write or export handoff files
- write to a database
- activate ingestion
- activate schedulers
- mutate production

Candidate fields include:

- dataset
- source_vendor
- source_dataset
- asset_type
- symbol
- trade_date
- open
- high
- low
- close
- volume
- transactions
- adjusted_status
- source_file_sha256
- source_file_size_bytes
- quarantine_path
- preview_only

The preview intentionally stops short of any warehouse writer, API route, or exported artifact.
That later step remains deferred to a separate approval flow after this local-only contract review is complete.
