# OPEX Calendar Verification

This document records the deterministic OPEX event-calendar verification slice.
It is documentation only.

## Verified Results

- 2026 full-year generation produced 12 events.
- June 2026 produced 1 event.
- June 2026 OPEX date is `2026-06-19`.
- `valid_count=12/12` for the full year.
- `no_vendor_calls=True`
- `no_db_writes=True`
- `event_id` format is `OPEX-YYYY-MM-DD`
- `timezone` is `America/New_York`
- `source` is `manual_rule`

## Boundary

This verification does not enable persistence.
It does not add scheduler behavior, vendor calls, database writes, or AI/trading/risk/signal/regime/portfolio logic.

