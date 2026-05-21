# Core Runtime

This document describes the core runtime foundation for `ai-market-machine-ingestion`.

## Scope

The runtime layer provides:

- environment-based configuration
- structured logging setup
- ingestion-focused exception types
- runtime context helpers
- database connection configuration only
- internal runtime datatypes

## Out Of Scope

The runtime layer does not provide:

- vendor clients
- writers
- backfills
- schedulers
- ingestion pipelines
- canonical schema or migrations
- AI or trading logic

## Boundary Notes

Database support in this layer is configuration-only. It does not create tables, run migrations, or write data directly.
