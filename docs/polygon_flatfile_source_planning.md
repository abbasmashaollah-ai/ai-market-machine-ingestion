# Polygon Flat-File Source Planning

`scripts.diagnose_polygon_flatfile_readiness.py` is the read-only planning diagnostic for the future Polygon flat-file path.

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

Discovery dry-runs should use [Polygon Flat-File Discovery Planning](polygon_flatfile_discovery_planning.md) and must treat the candidate path layout as provisional until reconciled with the official Polygon flat-file layout.

## Safety

The diagnostic does not:

- call Polygon
- call S3
- require `POLYGON_API_KEY`
- require `DATABASE_URL`
- read or write storage
- add AI, trading, risk, signal, regime, portfolio, strategy, or prediction logic

`ai-market-machine-data` remains the schema owner.
