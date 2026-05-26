# Event Calendar Evidence Plan

This is the evidence planning layer for the future persistence contract.

Planned checks after persistence exists:
- event row counts by event_type
- latest event_date by event_type
- missing event_type coverage
- timezone completeness
- missing title count
- missing source count
- symbol coverage for earnings_date events
- run/quality/lineage once persistence exists

Current boundary:
- no DB reads yet
- no DB writes yet
- the persistence contract must be approved before evidence-store wiring is added
