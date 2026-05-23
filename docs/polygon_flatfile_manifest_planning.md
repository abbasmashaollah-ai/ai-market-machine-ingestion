# Polygon Flat-File Manifest Planning

This document defines the manifest shape that will bridge flat-file storage and downstream evidence.

## Manifest role

- manifest is required before download enablement
- manifest is the bridge between flat-file storage and downstream evidence
- manifest must not replace run_history, quality, or lineage stores
- manifest should feed those stores later
- manifest must record integrity status
- manifest must record quarantine status and reason
- manifest planning is required before download enablement

## Planned fields

- `source_mode`
- `dataset`
- `asset_class`
- `timeframe`
- `object_key`
- `local_raw_path`
- `local_staging_path`
- `checksum`
- `size_bytes`
- `discovered_at`
- `downloaded_at`
- `parsed_at`
- `validation_status`
- `quarantine_status`
- `lineage_status`
- `integrity_status`

Quarantine handling is defined in [Polygon Flat-File Quarantine Policy](polygon_flatfile_quarantine_policy.md).

## Safety

This planning document does not:

- call Polygon
- call S3
- download files
- write files
- write to the database
- add scheduler behavior
- add API routes
- add AI, trading, risk, signal, regime, portfolio, strategy, or prediction logic

Integrity policy is defined in [Polygon Flat-File Integrity Policy](polygon_flatfile_integrity_policy.md).

Download planning is defined in [Polygon Flat-File Download Planning](polygon_flatfile_download_planning.md).

Persistence planning is defined in [Polygon Flat-File Persistence Planning](polygon_flatfile_persistence_planning.md).

`ai-market-machine-data` remains the schema owner.
