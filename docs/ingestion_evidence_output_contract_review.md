# Ingestion Evidence Output Contract Review

This document reviews the ingestion-side evidence outputs that support stored evidence health in `ai-market-machine-data`.

## Intended direction

This is an ingestion-side review only.

`ai-market-machine-data` defines canonical standards.
`ai-market-machine-ingestion` enforces runtime contracts and emits evidence.

Ingestion should not own canonical schema definitions.

The evidence outputs from ingestion should support:

- stored evidence health in data
- future Grafana/read models
- operator runbooks
- production scheduler readiness

## Required evidence output families

Ingestion should be able to emit:

- ingestion run history
- data quality results
- data lineage records
- evidence-chain verification
- coverage or freshness evidence
- checkpoint state
- vendor request or quota evidence
- error and retry evidence

## Safety

This review makes no runtime behavior changes.
It does not run ingestion, call vendors, read or write the database, or change scheduler behavior.
It does not introduce canonical schema ownership into ingestion.
No AI, trading, risk, signal, regime, or portfolio logic belongs in this contract review.
