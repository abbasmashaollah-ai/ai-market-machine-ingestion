# FRED Macro Vertical Slice Plan

Purpose:
- establish the FRED macro ingestion foundation as a dry-run/planning slice
- keep the data contract explicit before any persistence path is enabled

Dependencies:
- data repo contract confirmation
- vendor adapter alignment for FRED series fetches

Planned vendor adapter:
- read FRED series metadata and observations
- normalize series into the macro record shape used by the ingestion layer

Normalized macro record shape:
- series_id
- observation_date
- value
- source
- unit
- frequency
- notes

Starter series:
- DGS10
- DGS2
- FEDFUNDS
- CPIAUCSL
- UNRATE

Validation expectations:
- deterministic normalization
- explicit missing-series reporting
- quality checks on date/value presence
- no silent schema expansion

Boundary:
- writer/store integration is deferred until the data contract is confirmed
- preflight, runner, and evidence reporting should follow the existing manual ingestion pattern
- no AI/trading/risk/signal/regime logic belongs in this slice
