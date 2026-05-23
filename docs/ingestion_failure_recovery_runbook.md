# Ingestion Failure Recovery Runbook

This document maps ingestion failure classes to safe operator actions and diagnostics.

## Purpose

Use this runbook to decide what to inspect or rerun after a failure, without introducing automatic execution.

## Failure mappings

- `rate_limit`: reduce scope, wait, rerun with lower max requests
- `vendor_http_error`: retry later, inspect vendor status manually
- `validation_failed`: inspect quality results, manual review
- `coverage_missing`: run coverage diagnostic, gap fill if valid trading day
- `checkpoint_missing`: inspect checkpoint, resume cautiously
- `lineage_missing`: run evidence-chain verifier, rebuild evidence if needed
- `quality_failed`: inspect quality results, manual review
- `storage_integrity_failed`: quarantine, manual review
- `parse_failed`: quarantine, manual review

## Safe commands

Recommended commands are read-only diagnostics or operator helpers. They do not include secrets or destructive flags by default.

- `scripts.diagnose_polygon_quota_readiness`
- `scripts.inspect_data_quality_results`
- `scripts.diagnose_ohlcv_coverage`
- `scripts.fill_polygon_ohlcv_gaps`
- `scripts.inspect_polygon_ohlcv_checkpoint`
- `scripts.verify_polygon_ohlcv_evidence_chain`

## Safety

This document does not:

- execute commands
- call vendors
- write to the database
- enable the scheduler
- add API routes
- add AI, trading, risk, signal, regime, portfolio, strategy, or prediction logic

`ai-market-machine-data` remains the schema owner.
