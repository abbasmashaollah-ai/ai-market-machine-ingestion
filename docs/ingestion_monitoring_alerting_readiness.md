# Ingestion Monitoring and Alerting Readiness

This document defines the monitoring and alerting requirements before production scheduler enablement or larger-scale automation.

## Requirements

- monitoring is required before production scheduler enablement
- alerts should be based on run history, quality, lineage, evidence-chain checks, coverage, and quota or rate-limit signals
- no alert transport is implemented yet
- future alert transports may include logs, email, Slack/Discord, or dashboard hooks
- monitoring must not introduce trading or AI decision logic

## Required alerts

- failed run
- rate limit
- missing coverage
- quality failed
- lineage missing
- scheduler disabled
- scheduler blocked

## Required metrics

- rows fetched
- rows written
- rows rejected
- error count
- coverage ratio
- latency seconds
- request count

## Safety

This document does not:

- call vendors
- write to the database
- enable the scheduler
- add API routes
- add AI, trading, risk, signal, regime, portfolio, strategy, or prediction logic

`ai-market-machine-data` remains the schema owner.
