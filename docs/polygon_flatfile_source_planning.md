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

## Safety

The diagnostic does not:

- call Polygon
- call S3
- require `POLYGON_API_KEY`
- require `DATABASE_URL`
- read or write storage
- add AI, trading, risk, signal, regime, portfolio, strategy, or prediction logic

`ai-market-machine-data` remains the schema owner.
