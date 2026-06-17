# Polygon Stock Day Agg Remote Listing Readiness Check

This document explains the readiness checker for a metadata-only Polygon stock day aggregate remote listing probe.

## Purpose

The checker exists to verify local dependency and configuration readiness before a metadata-only vendor listing probe is attempted.

It does not approve production.

## What It Checks

The checker only checks:

- whether `boto3` is importable
- whether Polygon flat-file configuration names are present
- whether credentials are present by name only
- whether endpoint, bucket, and stock day aggregate prefix names are configured
- whether it is safe to attempt a metadata-only listing probe

It never prints secret values.

## What It Does Not Do

The checker does not:

- call vendors
- list remote objects
- download files
- generate quarantine artifacts
- generate handoff artifacts
- generate intake descriptors
- write DB
- run migrations
- activate schedulers
- mutate `ai-market-machine-data`
- touch the production warehouse
- print secrets

## Readiness Status

- `READY_FOR_METADATA_LISTING`
- `BLOCKED_MISSING_DEPENDENCY`
- `BLOCKED_MISSING_CONFIG`
- `BLOCKED_MISSING_CREDENTIALS`

If ready, the next gate remains the metadata-only vendor listing probe retry, not a download.

## Safety

Secrets are checked by presence only and never printed.

The checker returns JSON to stdout and does not write to `outputs/`.

