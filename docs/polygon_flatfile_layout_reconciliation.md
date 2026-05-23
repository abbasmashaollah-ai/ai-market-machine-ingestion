# Polygon Flat-File Layout Reconciliation

This document defines the planning boundary between the current provisional flat-file layout and the official Polygon flat-file layout that must be verified before any live work.

## Status

- current layout: provisional
- official layout verified: false
- live discovery enabled: false
- live download enabled: false

## Required order

1. Obtain the official Polygon flat-file layout.
2. Map dataset paths to the official structure.
3. Add mocked layout tests.
4. Add download dry-run coverage.
5. Only then evaluate discovery-only live access against official paths.
6. Follow with a download dry-run.
7. Follow with a parse dry-run.
8. Add persistence only after parse, validation, and evidence-design are complete.

## Safety boundary

Until the official layout is verified, no live flat-file discovery or download should run.

This planning layer does not:

- call Polygon
- call S3
- download files
- read or write files
- write to the database
- add scheduler behavior
- add API routes
- add AI, trading, risk, signal, regime, portfolio, strategy, or prediction logic

`ai-market-machine-data` remains the schema owner.
