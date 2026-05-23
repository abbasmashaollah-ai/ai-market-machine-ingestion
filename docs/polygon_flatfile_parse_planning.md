# Polygon Flat-File Parse Planning

This document defines the parse dry-run boundary for Polygon flat files.

## Parse order

- parse dry-run comes after download dry-run and integrity pass
- parser must feed shared OHLCV normalization, validation, and writer
- parser must not create a separate canonical path
- parse failures go to quarantine
- persistence comes only after parse dry-run plus validation and evidence-design
- parse happens only after integrity passes

Download planning is defined in [Polygon Flat-File Download Planning](polygon_flatfile_download_planning.md).

## Planned parser contract

- required input state: downloaded and integrity passed
- required columns: `symbol`, `timestamp`, `open`, `high`, `low`, `close`, `volume`
- normalization target: shared OHLCV normalization
- validation target: shared OHLCV validation
- writer target: shared OHLCV writer
- evidence target: run history, quality, lineage

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
