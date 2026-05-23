# Polygon Flat-File Integrity Policy

This document defines how flat-file downloads will be verified before parse or persistence is allowed.

## Policy

- downloaded files must pass checksum, size, and empty-file checks before parse
- invalid files go to quarantine
- manifest must record integrity status
- parse and persistence are blocked until integrity passes
- this policy remains planning-only until download implementation exists
- failed integrity or parse cases must be routed to quarantine

## Required checks

- checksum check
- size check
- empty-file check
- schema probe

## Quarantine

Files that fail integrity checks must be routed to quarantine and excluded from parse and downstream persistence until they are reviewed.

See [Polygon Flat-File Quarantine Policy](polygon_flatfile_quarantine_policy.md) for the quarantine boundary.

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
