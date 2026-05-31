# Options Evidence Plan

This is the evidence planning layer for the future persistence contract.

Planned checks after persistence exists:
- row counts by `underlying_symbol`
- row counts by `option_type`
- row counts by `expiration_date`
- missing contract coverage
- missing bid/ask/last counts
- missing volume/open_interest counts
- stale expiration metadata checks
- run/quality/lineage once persistence exists

Current boundary:
- no DB reads yet
- no DB writes yet
- the persistence contract must be approved before evidence-store wiring is added
- the writer plan is deferred and does not enable persistence
