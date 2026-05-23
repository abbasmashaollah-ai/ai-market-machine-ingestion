# Polygon Flat-File Storage Policy

This document defines where future flat-file downloads would live and the safety rules around that storage.

## Policy

- no flat-file downloads until storage root is explicitly configured and reviewed
- downloaded vendor files must not be committed to git
- future storage subdirs: `raw`, `staging`, `parsed`, `quarantine`, `manifests`
- checksum and integrity policy is required before download enablement
- cleanup and retention policy is required before scale
- manifest planning is required before download enablement
- integrity policy must be reviewed before parse enablement

## Allowed future subdirs

- `raw`
- `staging`
- `parsed`
- `quarantine`
- `manifests`

## Forbidden locations

- `repo_root`
- `app`
- `scripts`
- `tests`
- `docs`

## Safety

This policy does not:

- call Polygon
- call S3
- download files
- write files
- write to the database
- add scheduler behavior
- add API routes
- add AI, trading, risk, signal, regime, portfolio, strategy, or prediction logic

`ai-market-machine-data` remains the schema owner.
