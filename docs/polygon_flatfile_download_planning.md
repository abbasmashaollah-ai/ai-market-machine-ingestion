# Polygon Flat-File Download Planning

This document defines the dry-run boundary for future Polygon flat-file downloads.

## Download order

- download dry-run comes after official layout verification and discovery planning
- live download remains disabled
- download does not imply parse or persistence
- manifest, integrity, and quarantine planning are mandatory before live download
- parse happens only after integrity passes

## Planned download contract

- official layout required
- credentials required
- storage root must be reviewed
- manifest required
- integrity required
- quarantine required
- parse after download is disabled during planning

## Safety

This planning document does not:

- call Polygon
- call S3
- download files
- read files
- write files
- write to the database
- add scheduler behavior
- add API routes
- add AI, trading, risk, signal, regime, portfolio, strategy, or prediction logic

`ai-market-machine-data` remains the schema owner.
