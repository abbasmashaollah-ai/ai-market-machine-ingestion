# Polygon Flat-File Config Readiness

This diagnostic documents whether the expected flat-file configuration variables are present in the environment.

## Expected environment variables

- `POLYGON_FLATFILE_ACCESS_KEY_ID`
- `POLYGON_FLATFILE_SECRET_ACCESS_KEY`
- `POLYGON_FLATFILE_BUCKET`
- `POLYGON_FLATFILE_ENDPOINT`
- `POLYGON_FLATFILE_REGION`
- `POLYGON_FLATFILE_STORAGE_ROOT`

## Readiness states

- `not_configured`: no expected flat-file config variables are present
- `partial_configured`: some expected variables are present
- `configured_but_disabled`: all expected variables are present, but live flat-file discovery/download remain disabled

## Safety

This document and the related diagnostic do not:

- call Polygon
- call S3
- download files
- write files
- require `DATABASE_URL`
- add AI, trading, risk, signal, regime, portfolio, strategy, or prediction logic

`ai-market-machine-data` remains the schema owner.
