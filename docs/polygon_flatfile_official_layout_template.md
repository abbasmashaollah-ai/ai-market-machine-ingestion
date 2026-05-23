# Polygon Flat-File Official Layout Template

Use this template to capture Polygon's official flat-file layout once it is obtained.

## Source documentation URL/reference

-

## Access method expected

-

## Bucket/root path

-

## Asset class path

-

## Dataset path

-

## Date partition convention

-

## File format

-

## Compression format

-

## Sample official object keys

-

## Required credentials/env vars

-

## Local storage policy

-

## Checksum/integrity fields if available

-

## Notes on API vs flatfiles vs websocket source split

- `polygon/api` remains the live path for recent/daily/gap data and small controlled backfills.
- `polygon/flatfiles` is the historical/backfill path that must match the official layout.
- `polygon/websocket` is the future live streaming path.

## Status

official_layout_captured=false
official_layout_verified=false
live_discovery_allowed=false
live_download_allowed=false
