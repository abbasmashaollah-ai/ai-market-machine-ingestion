# News/Sentiment Evidence Plan

This is the evidence planning layer for the future persistence contract.

Planned checks after persistence exists:
- row counts by `source`
- row counts by `ticker`
- missing title count
- missing published_at count
- missing URL count
- missing sentiment label/score counts
- stale news checks
- run/quality/lineage once persistence exists

Current boundary:
- no DB reads yet
- no DB writes yet
- the persistence contract must be approved before evidence-store wiring is added
- the writer plan is deferred and does not enable persistence
