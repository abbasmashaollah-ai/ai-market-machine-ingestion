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

## Price Feature Checkpoint

The price package now supports both close-only and OHLCV dry-run inputs.

OHLCV-derived outputs currently include:
- ATR
- dollar volume
- average dollar volume
- relative volume
- liquidity score

This remains dry-run only:
- no DB writes
- no vendor calls
- no live API calls
- no scheduler activation
- no data repo changes
- no AI Machine changes

`market_features` may consume price dry-run output downstream, but `prices` does not depend on `market_features`.
