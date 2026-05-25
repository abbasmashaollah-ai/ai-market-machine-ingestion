# Polygon Volatility Ingestion Mapping

This document records the Polygon volatility index mapping and dry-run planning logic now owned by `ai-market-machine-ingestion`.

## Scope

This module ports the useful mapping behavior out of the data repo and keeps it in the ingestion boundary:

- volatility index symbol mapping
  - `VIX` -> `I:VIX`
  - `VVIX` -> `I:VVIX`
  - `VXN` -> `I:VXN`
  - `RVX` -> `I:RVX`
- canonical/vendor symbol conversion
- payload validation
- payload-to-canonical record mapping
- batch dry-run/plan payloads
- adapter-based fetch hooks

## Boundary Rules

- no scheduler wiring
- no cron wiring
- no default database writes
- no default live fetch
- no AI, trading, regime, portfolio, or risk logic
- no imports from `ai-market-machine-data`

## Default Behavior

The default path is dry-run only.

Fetch only occurs when an explicit adapter is injected and fetch is explicitly enabled.

## Notes

This module is a mapping and planning utility. It does not own writer execution or checkpoint persistence.
