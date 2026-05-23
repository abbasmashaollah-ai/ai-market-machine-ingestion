# Polygon Flat-File Source Planning

`scripts.diagnose_polygon_flatfile_layout_readiness.py` is the read-only planning diagnostic for the future Polygon flat-file path.

## Source split

- `polygon/api` is the live path for recent/daily/gap data and small controlled backfills
- `polygon/flatfiles` is the future historical/backfill path
- `polygon/websocket` is the future live streaming path

All source paths must feed the same downstream normalization, validation, writer, checkpoint, run-history, quality, and lineage pipeline.

## Flat-file implementation path

Before any persistence work, flat-file support should begin with:

1. discovery
2. download dry-run
3. parse dry-run
4. validation against the same calendar and canonical coverage expectations used elsewhere

Only after those steps should persistence be considered.

The current layout is provisional. No live flat-file discovery or download should run until the official Polygon flat-file layout is verified. The first live step later should be discovery-only against official paths, followed by a download dry-run, then a parse dry-run. Persistence comes only after parse, validation, and evidence-design are complete.

Discovery dry-runs should use [Polygon Flat-File Discovery Planning](polygon_flatfile_discovery_planning.md) and must treat the candidate path layout as provisional until reconciled with the official Polygon flat-file layout. Use [Polygon Flat-File Layout Reconciliation](polygon_flatfile_layout_reconciliation.md) for the verification boundary. Use [Polygon Flat-File Official Layout Template](polygon_flatfile_official_layout_template.md) to capture the official path structure once obtained.

Before any live path is enabled, use [Polygon Flat-File Config Readiness](polygon_flatfile_config_readiness.md) to confirm the expected environment variables are present without exposing their values.

Before any flat-file download work, use [Polygon Flat-File Storage Policy](polygon_flatfile_storage_policy.md) to define the allowed storage root and the forbidden locations.

Before download enablement, define [Polygon Flat-File Manifest Planning](polygon_flatfile_manifest_planning.md) so the storage layer can feed downstream evidence later.

Before parse enablement, define [Polygon Flat-File Integrity Policy](polygon_flatfile_integrity_policy.md) so invalid files are quarantined and blocked from persistence.

Before any retry or replay behavior exists, define [Polygon Flat-File Quarantine Policy](polygon_flatfile_quarantine_policy.md).

Before any parser implementation exists, define [Polygon Flat-File Parse Planning](polygon_flatfile_parse_planning.md). Parse dry-run comes after download dry-run and integrity pass, and parse failures must route to quarantine.

Before any download implementation exists, define [Polygon Flat-File Download Planning](polygon_flatfile_download_planning.md). Download dry-run comes after official layout verification and discovery planning.

Before any persistence implementation exists, define [Polygon Flat-File Persistence Planning](polygon_flatfile_persistence_planning.md). Flat-file persistence must use the shared OHLCV writer and the same checkpoint, run_history, quality, and lineage flow as the API source.

## Safety

The diagnostic does not:

- call Polygon
- call S3
- require `POLYGON_API_KEY`
- require `DATABASE_URL`
- read or write storage
- add AI, trading, risk, signal, regime, portfolio, strategy, or prediction logic

`ai-market-machine-data` remains the schema owner.
