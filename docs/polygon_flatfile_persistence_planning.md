# Polygon Flat-File Persistence Planning

This document defines the readiness gate for writing parsed flat-file OHLCV records into the shared canonical pipeline.

## Persistence contract

- flat-file persistence must use the shared OHLCV writer
- no separate canonical path is allowed
- persistence is blocked until parse dry-run, validation, manifest, and evidence design are ready
- flat-file source must feed the same checkpoint, run_history, quality, and lineage flow as the API source

## Planned targets

- writer target: shared OHLCV writer
- checkpoint target: shared checkpoint store
- evidence target: run history, quality, lineage
- canonical table target: canonical OHLCV

## Safety

This planning document does not:

- call Polygon
- call S3
- download files
- read files
- write files
- write to the database
- add scheduler behavior
- add API routes
- add AI, trading, risk, signal, regime, portfolio, strategy, or prediction logic

`ai-market-machine-data` remains the schema owner.
