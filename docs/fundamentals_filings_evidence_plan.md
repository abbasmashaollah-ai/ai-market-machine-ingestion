# Fundamentals/Filings Evidence Plan

This is the evidence planning layer for the future persistence contract.

Planned checks after persistence exists:
- row counts by `record_family`
- row counts by `symbol`
- missing record families
- missing symbol coverage
- missing payload count
- stale report period checks
- run/quality/lineage once persistence exists

Current boundary:
- no DB reads yet
- no DB writes yet
- the persistence contract must be approved before evidence-store wiring is added
- the writer plan is deferred and does not enable persistence
