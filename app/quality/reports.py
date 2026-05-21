from __future__ import annotations

from app.quality.validators import BatchValidationSummary, ValidationResult, ValidationStatus


def validation_results_to_report(
    results: list[ValidationResult],
    summary: BatchValidationSummary,
) -> dict[str, object]:
    return {
        "total_checks": summary.total_checks,
        "passed_checks": summary.passed_checks,
        "failed_checks": summary.failed_checks,
        "warning_checks": summary.warning_checks,
        "failed": summary.failed,
        "results": [
            {
                "check_name": result.check_name,
                "status": result.status.value,
                "severity": result.severity.value,
                "message": result.message,
                "field_name": result.field_name,
                "details": result.details,
            }
            for result in results
        ],
        "overall_status": ValidationStatus.FAIL.value if summary.failed else ValidationStatus.PASS.value,
    }
