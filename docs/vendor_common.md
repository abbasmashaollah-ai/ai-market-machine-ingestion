# Vendor Common Infrastructure

This document covers the shared vendor infrastructure layer in `app/vendors/common/`.

## Scope

The vendor common layer provides:

- vendor exception types
- deterministic rate-limit helpers
- HTTP request and response metadata shapes
- an HTTP client abstraction only

## Out Of Scope

The vendor common layer does not provide:

- real Polygon clients
- real FRED clients
- vendor endpoint logic
- database writes
- canonical writers
- ingestion pipelines
- backfills
- schedulers
- API routes
- AI or trading logic

## Boundary Notes

This layer is intentionally abstract. It supports future vendor integrations without binding the repository to a specific external API or orchestration system.
