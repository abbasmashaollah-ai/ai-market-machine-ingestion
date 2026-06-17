# Polygon Stock Day Agg Ingestion Production Readiness Preflight

This document describes the read-only preflight used to verify whether the Polygon/Massive stock day aggregate ingestion path is ready for operator review.

## Purpose

The preflight gathers evidence about the local repository state for the stock OHLCV ingestion path. It is intended to confirm that the expected scripts, tests, and docs exist and that the path does not contain obvious production-risk mutations.

## What It Checks

The preflight checks for:

- required stock day aggregate ingestion scripts
- required tests for those scripts
- required documentation pages for the ingestion flow
- tracked generated artifacts under `outputs/`
- local signs of production database writes
- local signs of scheduler activation
- local signs of direct data repo mutation
- safe output policy, including no secret printing

## What It Does Not Do

The preflight does not:

- call Polygon
- call Massive
- download remote files
- write to the database
- run migrations
- activate schedulers
- mutate `ai-market-machine-data`
- touch production
- print secrets

Vendor credential names may be referenced by name only, but secret values must never be printed.

## Readiness Meaning

- `READY_FOR_OPERATOR_REVIEW` means all required evidence exists and no blocking risk was detected.
- `EVIDENCE_INCOMPLETE` means one or more required scripts, tests, or docs are missing.
- `BLOCKED` means tracked generated artifacts were found, or a production DB writer, scheduler activation, or direct data repo mutation was detected.

## Next Step

If the result is `READY_FOR_OPERATOR_REVIEW`, the next step is to prepare the ingestion operator approval package. It is not automatic production activation.

