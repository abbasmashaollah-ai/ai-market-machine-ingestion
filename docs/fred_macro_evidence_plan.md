# FRED Macro Evidence Plan

This is the evidence planning layer for the future persistence contract.

Planned checks after persistence exists:
- macro row counts by series
- latest observation date by series
- missing value counts
- run status
- quality status
- lineage status

Current boundary:
- no DB reads yet
- no DB writes yet
- the persistence contract must be approved before evidence-store wiring is added
