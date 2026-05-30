# Breadth/Participation Vertical Slice Plan

Purpose:
- define the next planning slice for breadth and participation metrics without introducing trading, strategy, or prediction logic
- keep breadth indicators as data-only inputs for later producer work

Target metrics:
- advance/decline counts
- new highs/new lows
- percent above moving averages
- up-volume/down-volume
- sector participation
- index/universe breadth

Dependency on symbol_master and ETF/index universe:
- the slice depends on symbol_master and the ETF/index universe as upstream reference layers
- symbol and universe mapping must be approved before any persistence work is considered

Likely source candidates:
- market data vendor if available
- exchange breadth feeds if available
- derived-from-OHLCV path later
- manual_fixture

Normalized record shape proposal:
- metric_id
- metric_type
- observation_date
- universe
- symbol optional
- value
- numerator
- denominator
- source
- notes

Quality expectations:
- deterministic normalization for fixed fixtures
- explicit missing-field reporting
- stable metric and universe naming
- no silent expansion of universe coverage
- preserve source identifiers, universe mappings, and observation dates in lineage evidence

Lineage expectations:
- preserve source and optional symbol on every normalized record
- keep the upstream metric type, universe, and observation date in lineage evidence where available
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
