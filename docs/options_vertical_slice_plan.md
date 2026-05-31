# Options Vertical Slice Plan

Purpose:
- define the next planning slice for options coverage without introducing trading, strategy, or prediction logic
- keep option chains, contract metadata, open interest, implied volatility, and put/call statistics as data-only inputs for later producer work

Target datasets:
- option chains
- option contracts
- open interest
- implied volatility
- put/call volume
- put/call open interest
- expiration metadata

Dependency on symbol_master:
- the slice depends on symbol_master for underlying symbol normalization and contract linkage
- underlying mapping must be approved before any persistence work is considered

Likely source candidates:
- Polygon
- Tradier
- OCC-derived sources
- manual_fixture

Normalized record shape proposal:
- contract_symbol
- underlying_symbol
- expiration_date
- strike
- option_type
- bid
- ask
- last
- volume
- open_interest
- implied_volatility
- source
- notes

Quality expectations:
- deterministic normalization for fixed fixtures
- explicit missing-field reporting
- stable contract and underlying naming
- no silent expansion of contract or expiration coverage
- preserve vendor contract symbols, underlying mappings, and expiration metadata in lineage evidence

Lineage expectations:
- preserve source and contract identifiers on every normalized record
- keep the upstream underlying symbol, expiration date, strike, and option type in lineage evidence where available
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
