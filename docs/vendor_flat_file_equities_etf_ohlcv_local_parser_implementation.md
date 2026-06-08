# Vendor Flat-File Equities ETF OHLCV Local Parser Implementation

## Purpose

- implement the local parser contract for synthetic Polygon-style equities/ETF daily OHLCV fixtures
- keep the parser local-file-only and side-effect free

## Implementation Summary

- local parser implementation exists
- synthetic fixtures only
- no runtime adapter
- no downloader
- no vendor calls
- no downloads
- no DB writes
- no scheduler activation
- no AI Machine runtime wiring
- parser output is not production evidence
- warehouse handoff comes later

## Safety Notes

- local files only
- pure function style where possible
- no env vars read
- no requests/http/vendor SDK imports
- no DB or writer imports
- no output files written

## Handoff Position

- the parser consumes fixture CSV + adjacent manifest
- the parser validates checksum before parsing
- the parser normalizes rows into the documented contract shape
- warehouse handoff comes after parser + normalization validation
- AI Machine consumes only certified Data API/evidence
