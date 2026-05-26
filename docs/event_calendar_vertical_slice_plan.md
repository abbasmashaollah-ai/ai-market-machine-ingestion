# Event Calendar Vertical Slice Plan

Purpose:
- define the next planning slice for calendar-driven market events without introducing interpretation logic
- keep macro events, scheduled releases, and earnings dates as data-only inputs for later producer work

Target event types:
- CPI
- FOMC
- NFP
- OPEX
- earnings dates

Likely source candidates:
- FRED, BLS, and Fed official sources for macro events
- Nasdaq, FMP, and Finnhub for earnings calendar data if available
- manual fixture for deterministic tests

Data repo contract dependency:
- the canonical event-calendar storage contract must exist in `ai-market-machine-data` before any persistence design is approved
- this repo stays at planning and producer-boundary definition only until that contract exists

Normalized event record shape:
- event_id
- event_type
- event_date
- event_time
- timezone
- source
- symbol optional
- title
- importance
- notes

Quality expectations:
- deterministic normalization for fixed fixtures
- explicit missing-field reporting
- source and event_type must remain stable
- no silent event-type expansion
- event_date and timezone should be validated together when time is present

Lineage expectations:
- preserve source and optional symbol on every normalized record
- keep the upstream event title and event_id in lineage evidence where available
- surface missing or partial event coverage explicitly in evidence output

Preflight/runner/evidence pattern:
- provide a read-only preflight command before any writer boundary exists
- provide a manual runner only after the data contract is approved
- verify the slice with a read-only evidence command before any persistence work is considered

Boundary:
- no AI/trading/risk/signal/regime/portfolio logic
- no DB writes
- no scheduler
- no FastAPI routes
- no migrations
- no schema ownership
- no vendor calls in documentation or verification-only steps
