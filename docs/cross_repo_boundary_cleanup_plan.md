# Cross-Repo Boundary Cleanup Plan

This document classifies the overlap reported by the boundary audit.

## Rules

- no cleanup should be destructive until both repos are audited
- `ai-market-machine-data` owns schema, read APIs, and Grafana read models
- `ai-market-machine-ingestion` owns runtime ingestion, scheduler execution, and vendor fetching
- the data repo may expose stored health from evidence, not live vendor ingestion

## Classifications

- keep in data: schema, migrations, canonical read APIs, Grafana read models, stored evidence health
- move to ingestion: vendor fetching, daily runners, backfills, flat files, websocket, scheduler execution
- deprecate in data: direct vendor ingestion, old runtime ingestion paths, direct scheduler execution
- hygiene cleanup: `.env`, `.venv`, `.pytest_cache`, `__pycache__`, logs in handoff zips

## Safety

This cleanup plan does not:

- move files
- delete files
- call vendors
- write to the database
- change scheduler behavior
- change API behavior
- add schema changes or migrations
- add AI, trading, risk, signal, regime, or portfolio logic

