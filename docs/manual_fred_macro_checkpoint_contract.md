# Manual FRED Macro Checkpoint Contract

This document defines the in-memory checkpoint state record for manual FRED macro incremental runs.

## Scope

The checkpoint contract represents future manual incremental progress only.

It does not:

- persist state
- execute jobs
- call vendors
- write to the database
- schedule work
- create tables
- run migrations

## Fields

- `checkpoint_key`
- `vendor`
- `dataset`
- `series_id`
- `timeframe`
- `planned_start_date`
- `planned_end_date`
- `last_successful_observation_date` optional
- `status`
- `created_at`
- `updated_at`

## Status Values

- `planned`
- `ready`
- `completed`
- `failed`

## Boundary

`ai-market-machine-data` remains the schema owner.

This repository keeps the checkpoint contract in memory only and routes future writes through `app/writers/` if they are later approved.
