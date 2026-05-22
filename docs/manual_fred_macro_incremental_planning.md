# Manual FRED Macro Incremental Planning

This document defines the manual planning layer for future incremental FRED macro updates.

## Scope

The planning layer only determines what would run and how checkpoint/run metadata is represented.

It does not:

- fetch vendor data
- validate or persist data
- execute jobs
- schedule anything
- write to the database

## Planned Responsibility

The planning layer creates deterministic manual plans for:

- selected FRED macro series
- job metadata
- run metadata
- checkpoint keys

## Checkpoint Shape

Checkpoint keys are built from:

- vendor
- dataset
- symbol
- timeframe
- start date
- end date

This keeps future incremental updates resumable without adding scheduler behavior.

## Boundary

`ai-market-machine-data` remains the schema owner.

This repository only plans ingestion work and routes any future writes through `app/writers/`.
