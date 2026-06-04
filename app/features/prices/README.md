# prices

Deterministic price evidence helpers for dry-run use only.

This package now includes the dry-run path from fixture closes through observation building, validator, mock writer, and report generation. Real writer and persistence behavior stays deferred.

The package remains dry-run only:
- no DB writes
- no vendor calls
- no scheduler activation

Supported dry-run input modes:
- close-history rows or close-only sequences
- OHLCV rows with `date`, `open`, `high`, `low`, `close`, and `volume` when available
