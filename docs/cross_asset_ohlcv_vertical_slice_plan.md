# Cross-Asset OHLCV Vertical Slice Plan

Purpose:
- define the next planning slice for cross-asset OHLCV coverage without introducing trading, strategy, or prediction logic
- keep bonds/rates proxies, DXY / dollar index proxies, commodities, crypto, and FX as data-only inputs for later producer work

Target groups:
- bonds/rates proxies
- DXY / dollar index proxy
- commodities
- crypto
- FX

Dependency on symbol_master or separate asset-master planning:
- the slice depends on symbol_master or a separately approved asset-master planning path
- cross-asset symbol resolution and asset grouping must be approved before any persistence work is considered

Reuse of existing OHLCV normalization/writer pattern:
- reuse the existing OHLCV normalization and writer pattern only after the data-side contracts are approved
- do not introduce a separate persistence contract here

Likely source candidates:
- Polygon
- FMP
- vendor-specific FX/crypto sources later
- manual_fixture

Normalized record shape:
- align to the existing OHLCV contract

Quality expectations:
- deterministic normalization for fixed fixtures
- explicit missing-field reporting
- stable source naming and asset grouping
- no silent expansion of symbol or asset coverage
- preserve vendor symbol mapping, source, and market date lineage in evidence

Lineage expectations:
- preserve source and optional symbol/asset identifiers on every normalized record
- keep the upstream timestamp, market date, and vendor symbol mapping in lineage evidence where available
- surface missing or partial coverage explicitly in evidence output

Preflight/runner/evidence pattern:
- provide a read-only preflight command before any writer boundary exists
- provide a manual runner only after the data contract is approved
- verify the slice with a read-only evidence command before any persistence work is considered

Persistence deferred until symbol/asset scope is approved:
- no storage contract is assumed here
- no DB writes, migrations, or schema ownership are introduced
- the repo remains at planning and producer-boundary definition only until symbol/asset scope is approved

Boundary:
- no AI/trading/risk/signal/regime/portfolio logic
- no DB reads
- no DB writes
- no scheduler
- no FastAPI routes
- no migrations
- no schema ownership
- no vendor calls in documentation or verification-only steps
