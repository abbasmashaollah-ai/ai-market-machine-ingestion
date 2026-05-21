from __future__ import annotations

from dataclasses import dataclass

from app.quality.validators import ValidationResult, fail_result, pass_result


@dataclass(frozen=True)
class ReconciliationSummary:
    expected_count: int
    received_count: int
    missing_count: int
    excess_count: int


def summarize_counts(expected_count: int, received_count: int) -> ReconciliationSummary:
    missing_count = max(expected_count - received_count, 0)
    excess_count = max(received_count - expected_count, 0)
    return ReconciliationSummary(
        expected_count=expected_count,
        received_count=received_count,
        missing_count=missing_count,
        excess_count=excess_count,
    )


def reconcile_expected_vs_received(expected_count: int, received_count: int) -> list[ValidationResult]:
    summary = summarize_counts(expected_count, received_count)
    if summary.missing_count == 0 and summary.excess_count == 0:
        return [pass_result("reconciliation_counts", "expected and received counts match")]
    return [
        fail_result(
            "reconciliation_counts",
            "expected and received counts differ",
            expected_count=summary.expected_count,
            received_count=summary.received_count,
            missing_count=summary.missing_count,
            excess_count=summary.excess_count,
        )
    ]
