# Vendor Flat-File Equities ETF OHLCV Fixture Checkpoint

## Purpose

- document tiny synthetic fixture samples for equities and ETF daily OHLCV
- keep the flat-file contract testable without vendor activation

## Fixture Summary

- equities sample includes AAPL, MSFT, and NVDA
- ETF sample includes SPY, QQQ, IWM, DIA, and XLK
- both samples are synthetic fixture only, not vendor data, not production evidence
- manifests sit next to the raw CSV files
- SHA256 is verified and required before normalization
- no checksum, no certification

## What This Proves

- tiny synthetic fixture samples exist
- equities and ETF daily OHLCV samples follow the contract
- manifest next to raw files is supported
- validator exists for CSV plus manifest checks
- fixtures are not real vendor data
- fixtures are not production evidence

## What This Does Not Mean

- no runtime adapter
- no downloader
- no vendor calls
- no downloads
- no DB writes
- no ingestion run
- no scheduler activation
- no AI Machine runtime wiring

## Next Step

- local parser contract, not runtime downloader

## Safety Confirmations

- no vendor calls
- no downloads
- no DB writes
- no ingestion run
- no scheduler activation
- no production changes
- no AI Machine runtime wiring
- no secrets committed
