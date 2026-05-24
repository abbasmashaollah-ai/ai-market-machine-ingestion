# Cross-Repo Boundary Overlap Audit

This audit documents the boundary between `ai-market-machine-data` and `ai-market-machine-ingestion`.

## Ownership

- `ai-market-machine-data` owns schema, migrations, canonical read APIs, and Grafana/read models
- `ai-market-machine-ingestion` owns vendor fetching, daily runners, backfills, flat files, websocket work, and scheduler execution

## Boundary intent

The data repo should eventually expose last-known vendor and ingestion health from stored evidence. It should not run vendor ingestion directly.

No AI, trading, risk, signal, regime, or portfolio logic belongs in the data repo.
Canonical standards are defined in `ai-market-machine-data` and enforced at runtime in `ai-market-machine-ingestion`.

## Audit scope

The diagnostic tracks:

- data-owned schema paths
- data-owned read API paths
- data-owned monitoring paths
- ingestion runtime overlap
- ingestion scheduler overlap
- ingestion vendor-client overlap
- ingestion mutation endpoint overlap
- legacy or deprecate paths
- packaging hygiene issues

## Canonical Contract Boundary

- data defines canonical standards
- ingestion enforces canonical standards at runtime
- ingestion must not define canonical schema, timestamp authority, or lineage contract authority

## Safety

This audit is read-only. It does not:

- call vendors
- write to the database
- change scheduler behavior
- change API behavior
- add schema changes or migrations
- add AI, trading, risk, signal, regime, or portfolio logic

The cleanup plan is documented in [Cross-Repo Boundary Cleanup Plan](cross_repo_boundary_cleanup_plan.md).
