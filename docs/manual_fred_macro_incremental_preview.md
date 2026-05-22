# Manual FRED Macro Incremental Preview

This document defines the in-memory preview layer for future manual FRED macro incremental runs.

## Scope

The preview layer combines:

- the manual FRED macro incremental plan
- checkpoint state records
- initial run result records with zero counts

It does not:

- execute anything
- call vendors
- write to the database
- schedule jobs
- create tables
- run migrations

## Boundary

`ai-market-machine-data` remains the schema owner.

This repository only previews what a manual incremental run would prepare in memory.
