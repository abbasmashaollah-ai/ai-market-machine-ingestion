# Fundamentals/Filings Vertical Slice Plan

Purpose:
- define the next planning slice for company fundamentals and SEC filings without introducing interpretation or trading logic
- keep company profile data, financial statements, ratios/metrics, earnings estimates, and filings as data-only inputs for later producer work

Target domains:
- company profile
- financial statements
- ratios/metrics
- earnings estimates
- SEC filings

Dependency on symbol_master:
- the slice depends on symbol_master as the canonical symbol and identifier foundation
- symbol resolution, symbol normalization, and symbol presence checks must align with the approved symbol_master contract before any persistence work is considered

Likely source candidates:
- SEC
- FMP
- Finnhub
- manual_fixture

Normalized record families:
- company_profile
- financial_statement
- financial_metric
- earnings_estimate
- sec_filing

Quality expectations:
- deterministic normalization for fixed fixtures
- explicit missing-field reporting
- stable source naming and record-family naming
- no silent expansion of record families
- preserve report period, symbol, and source identifiers in lineage evidence

Lineage expectations:
- preserve source and optional symbol on every normalized record
- keep filing accession, form type, filing date, and vendor request context where available
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
