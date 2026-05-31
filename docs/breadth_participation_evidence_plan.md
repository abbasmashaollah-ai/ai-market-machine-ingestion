# Breadth/Participation Evidence Plan

This is the evidence planning layer for the future persistence contract.

Planned checks after persistence exists:
- row counts by `metric_type`
- row counts by `universe`
- missing metric types
- missing universe coverage
- missing numerator/denominator count
- stale `observation_date` checks
- run/quality/lineage once persistence exists

Current boundary:
- no DB reads yet
- no DB writes yet
- the persistence contract must be approved before evidence-store wiring is added
- the writer plan is deferred and does not enable persistence
