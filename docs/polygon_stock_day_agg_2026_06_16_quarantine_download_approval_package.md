# Polygon Stock Day Agg 2026-06-16 Quarantine Download Approval Package

This document requests approval to download the confirmed `2026-06-16` Polygon stock day aggregate file into local quarantine only.

It does not approve parse, normalization, handoff generation, intake package generation, or any downstream repo mutation.

## Purpose

Request approval to download the confirmed `2026-06-16` Polygon stock day aggregate file into local quarantine only.

## Evidence Basis

- Manual probe evidence commit: `89ca6da`
- `object_present true`
- `redacted_key_tail 2026/06/2026-06-16.csv.gz`
- `size_bytes 316221`
- `listed_key_sha256_prefix a988421953a6`
- `resolved_key_sha256_prefix a988421953a6`
- No prior download occurred

## Approved Scope

- One file only
- Date: `2026-06-16`
- Dataset type: `daily_ohlcv`
- Source: Polygon/Massive flat files
- Destination: local quarantine path only
- Compute local file hash and size after download
- Write/download evidence doc only after operator-approved execution

## Proposed Quarantine Path

- `outputs/quarantine/polygon_flat_files/polygon_stocks_day_aggs_2026-06-16.csv.gz`

## Approval Phrase

`APPROVE POLYGON STOCK DAY AGG 2026-06-16 QUARANTINE DOWNLOAD`

## Operator Approval Record Template

- Approval phrase
- Approver
- Date/time
- Target date `2026-06-16`
- Expected filename `2026-06-16.csv.gz`
- Expected redacted key tail
- Expected size from probe
- Scope
- Non-authorized actions
- Required post-download evidence

## Required Post-Download Evidence

- Command used
- Target date
- Source redacted key tail
- Local quarantine path
- Local file exists
- Local file size
- Local sha256
- Expected/probe size comparison
- No parse confirmation
- No normalization confirmation
- No handoff/intake generation confirmation
- No DB write confirmation
- No scheduler/backfill confirmation
- No AI wiring confirmation
- No secrets printed confirmation
- Unrelated untracked files untouched

## Not Authorized by This Package

- Parsing
- Normalization
- Handoff candidate generation
- Intake package generation
- Data repo mutation
- DB write
- Production staging load
- Canonical promotion
- Scheduler/backfill
- AI wiring
- Generated output commit
- Unrelated untracked file staging/deletion
- Printing secrets or DB URLs

## Next Step

- After this approval package, create an operator approval record
- Only after approval record, execute one quarantine download
- After download evidence, create parse/normalization/handoff approval package

## Completion Statement

This package records approval intent for a single-file quarantine download and nothing beyond that scope.
