# Ingestion Retry and Recovery Readiness

This document defines how failed ingestion runs should be retried, resumed, skipped, quarantined, or manually reviewed.

## Requirements

- retry and recovery is required before production scheduler enablement
- automatic retry is disabled for now
- recovery must use checkpoints, run history, quality, lineage, and evidence verification
- rate-limit retry must be conservative and never aggressive
- flat-file failures may require quarantine and manual review
- retry and recovery must not introduce trading or AI decision logic
- failure-class mappings live in [Ingestion Failure Recovery Runbook](ingestion_failure_recovery_runbook.md)

## Required failure classes

- rate limit
- vendor HTTP error
- validation failed
- coverage missing
- checkpoint missing
- lineage missing
- quality failed
- storage integrity failed
- parse failed

## Required recovery actions

- retry later
- resume from checkpoint
- reduce scope
- quarantine
- manual review
- skip non-trading day
- rebuild evidence

## Safety

This document does not:

- call vendors
- write to the database
- enable the scheduler
- add API routes
- add AI, trading, risk, signal, regime, portfolio, strategy, or prediction logic

`ai-market-machine-data` remains the schema owner.
