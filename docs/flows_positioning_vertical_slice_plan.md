# Flows/Positioning Vertical Slice Plan

Purpose:
- define the next planning slice for flows and positioning coverage without introducing trading, strategy, or prediction logic
- keep ETF flows, fund flows, short interest, institutional positioning, and CFTC/COT data as inputs for later producer work

Target datasets:
- ETF flows
- fund flows
- short interest
- institutional positioning
- CFTC/COT positioning
- dark pool/off-exchange volume if accessible later

Dependency on symbol_master and ETF/index universe:
- the slice depends on symbol_master and the ETF/index universe as upstream reference layers
- symbol and universe mapping must be approved before any persistence work is considered

Likely source candidates:
- FMP
- FINRA
- CFTC
- ETF issuer/public datasets
- vendor_flow_feed
- manual_fixture

Normalized record shape proposal:
- record_id
- record_type
- observation_date
- symbol
- asset_class
- value
- unit
- source
- raw_source_id
- notes

Quality expectations:
- deterministic normalization for fixed fixtures
- explicit missing-field reporting
- stable record and asset-class naming
- no silent expansion of flow or positioning coverage
- preserve source identifiers, symbol mappings, and observation dates in lineage evidence

Lineage expectations:
- preserve source and optional symbol on every normalized record
- keep the upstream record type, asset class, and observation date in lineage evidence where available
- surface missing or partial coverage explicitly in evidence output

Preflight/runner/evidence pattern:
- provide a read-only preflight command before any writer boundary exists
- provide a manual runner only after the data contract is approved
- verify the slice with a read-only evidence command before any persistence work is considered

Persistence deferred until data-side contracts are approved:
- no storage contract is assumed here
- no DB writes, migrations, or schema ownership are introduced
- the repo remains at planning and producer-boundary definition only until the data-side contract exists

Boundary:
- no AI/trading/risk/signal/regime/portfolio logic
- no DB reads
- no DB writes
- no scheduler
- no FastAPI routes
- no migrations
- no schema ownership
- no vendor calls in documentation or verification-only steps
