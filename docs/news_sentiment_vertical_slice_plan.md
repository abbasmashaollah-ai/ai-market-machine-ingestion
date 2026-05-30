# News/Sentiment Vertical Slice Plan

Purpose:
- define the next planning slice for news and sentiment without introducing trading or interpretation logic
- keep headlines, article summaries, publisher metadata, timestamps, related tickers, and vendor sentiment as data-only inputs for later producer work

Target records:
- headline
- article summary
- source/publisher
- published_at
- related tickers
- sentiment label if vendor-provided
- sentiment score if vendor-provided
- url/source_id

Dependency on symbol_master:
- the slice depends on symbol_master for ticker mapping and ticker normalization
- related ticker values must align to the approved symbol_master contract before any persistence work is considered

Likely source candidates:
- Finnhub
- FMP
- Polygon news if available
- manual_fixture

Normalized record shape proposal:
- news_id
- published_at
- source
- publisher
- title
- summary
- url
- tickers
- sentiment_label
- sentiment_score
- raw_source_id
- notes

Quality expectations:
- deterministic normalization for fixed fixtures
- explicit missing-field reporting
- stable source naming and record shape naming
- no silent expansion of ticker or sentiment fields
- preserve timestamps, publisher names, and raw source identifiers in lineage evidence

Lineage expectations:
- preserve source, raw_source_id, and related tickers on every normalized record
- keep the upstream title, URL, and published_at in lineage evidence where available
- surface missing or partial news coverage explicitly in evidence output

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
