# Polygon Stock Day Agg Quarantine Parse Inspection

This script is for local quarantine inspection only.

It reads a downloaded Polygon stock day aggregates gzip CSV from disk, parses the header and rows, and reports a safe JSON summary of the file structure and basic value quality.

It does not:

- call vendor APIs
- download remote files
- export handoff records
- write to a database
- activate ingestion
- activate schedulers
- mutate production

Reported fields include:

- requested date
- local file existence, size, and SHA256
- header fields and field count
- row count and sampled row count
- symbol counts and SPY / sector ETF presence
- date coverage
- basic numeric parse summaries for OHLCV-like columns when present

The inspection is intended to precede later local normalization and handoff-builder work.
It helps confirm the downloaded quarantine file is structurally close to the expected stock day aggregate shape before any warehouse contract mapping is introduced.
