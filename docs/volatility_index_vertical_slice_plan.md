# Volatility Index Vertical Slice Plan

Purpose:
- define the next market-data vertical slice after FRED macro verification
- keep the producer boundary explicit before any vendor, scheduler, or persistence work starts

Starter symbols:
- VIX
- VVIX
- VXN
- RVX

Likely source candidates:
- Polygon
- Cboe if later approved

Data repo contract dependency:
- the target data-side contract must exist before any writer/store integration is added
- producer work stays limited to the ingestion-repo boundary until that contract is confirmed

Normalized record shape proposal:
- symbol
- observation_date
- value
- source
- vendor_symbol
- unit
- notes

Quality expectations:
- deterministic normalization
- explicit missing-symbol reporting
- explicit missing-value reporting
- no silent schema expansion
- stable date/value handling across vendor variants

Lineage expectations:
- preserve source and vendor_symbol on every emitted record
- keep evidence tied to the normalized observation date and upstream vendor payload
- make missing or partial coverage visible in the evidence output

Preflight/runner/evidence pattern:
- provide a read-only preflight command before any write-capable path exists
- provide a manual runner that can emit evidence without requiring scheduler activation
- verify the slice with a read-only evidence command before considering persistence work

Boundary:
- no AI/trading/risk/signal/regime/portfolio logic
- no DB writes
- no scheduler
- no FastAPI routes
- no migrations
- no schema ownership
- no vendor calls in documentation or verification-only steps
