# Polygon Flat-File Discovery Planning

`scripts/plan_polygon_flatfile_discovery.py` is a dry-run planner for future Polygon flat-file discovery.

## Purpose

The planner computes provisional candidate object paths from:

- dataset
- asset class
- timeframe
- date range

It uses the current market calendar helper to determine expected trading days and does not connect to Polygon or S3.

## Candidate layout

The current candidate format is provisional:

`polygon/flatfiles/{asset_class}/{dataset}/{timeframe}/{YYYY-MM-DD}.parquet`

This must be reconciled against Polygon's official flat-file layout before any live use.

Use [Polygon Flat-File Layout Reconciliation](polygon_flatfile_layout_reconciliation.md) before any live discovery work.

## Safety

The planner does not:

- call Polygon
- call S3
- download files
- write files
- require `POLYGON_API_KEY`
- require `DATABASE_URL`
- add AI, trading, risk, signal, regime, portfolio, strategy, or prediction logic

`ai-market-machine-data` remains the schema owner.
