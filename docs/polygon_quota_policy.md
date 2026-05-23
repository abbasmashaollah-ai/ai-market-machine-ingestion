# Polygon Quota Policy

Polygon quota planning in this repository is split by source path:

- `api` for recent/daily/gap data and small controlled backfills
- `flatfiles` for large historical downloads/backfills
- `websocket` for future live streaming data

All source paths must feed the same normalization, validation, writer, checkpoint, run-history, quality, and lineage pipeline.

## Readiness

`scripts/diagnose_polygon_quota_readiness.py` is the read-only diagnostic for request budget planning.

## Safety

The repository does not currently enable Polygon automation by default.

`ai-market-machine-data` remains the schema owner.
