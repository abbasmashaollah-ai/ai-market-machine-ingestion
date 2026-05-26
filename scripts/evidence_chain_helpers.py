from __future__ import annotations

from datetime import date


def status_from_requirement(*, required: bool, present: bool, unexpected_warn: bool = True) -> str:
    if required:
        return "PASS" if present else "FAIL"
    if present and unexpected_warn:
        return "WARN"
    return "PASS"


def evidence_status_from_counts(
    *,
    canonical_count: int,
    run_count: int,
    quality_count: int,
    lineage_count: int,
    missing_dates: list[date],
) -> str:
    if canonical_count == 0 and run_count == 0 and quality_count == 0 and lineage_count == 0 and not missing_dates:
        return "missing"
    if canonical_count > 0 and run_count > 0 and quality_count > 0 and lineage_count > 0 and not missing_dates:
        return "complete"
    return "partial"
