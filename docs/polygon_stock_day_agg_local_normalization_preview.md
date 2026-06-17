# Polygon Stock Day Agg Local Normalization Preview

This script is for local quarantine normalization preview only.

It reads a downloaded Polygon stock day aggregates gzip CSV from disk, parses the rows, and converts valid rows into an in-memory preview shape that resembles the eventual normalized record layout.

It does not:

- call vendor APIs
- download remote files
- export warehouse handoff artifacts
- write to a database
- activate ingestion
- activate schedulers
- mutate production

The preview reports:

- requested date
- local file existence, size, and SHA256
- raw header fields and raw row count
- normalized candidate count and rejected row count
- rejection reason summary
- SPY and sector ETF coverage
- date coverage across normalized preview rows
- sample normalized rows, capped by `--sample-limit`
- numeric validation summary for OHLCV-like fields and transactions

Raw-to-preview mapping:

- `ticker` -> `symbol`
- requested date and/or parsed `window_start` -> `trade_date`
- `open`, `high`, `low`, `close`, `volume`, `transactions` -> same-named preview fields
- dataset metadata is attached as:
  - `source_dataset = polygon_stocks_day_aggs`
  - `source_vendor = polygon_massive_flat_files`
  - `adjusted_status = unknown_or_vendor_default`
  - `preview_only = true`

Final warehouse contract mapping is intentionally deferred.
This step exists to verify the downloaded quarantine file can be normalized safely in memory before any later writer or handoff builder is introduced.
