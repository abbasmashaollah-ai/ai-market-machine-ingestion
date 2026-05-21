from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ValidationSeverity(str, Enum):
    ERROR = "error"
    WARN = "warn"
    INFO = "info"


class ValidationStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"


@dataclass(frozen=True)
class ValidationResult:
    check_name: str
    status: ValidationStatus
    severity: ValidationSeverity
    message: str
    field_name: str | None = None
    details: dict[str, object] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.status == ValidationStatus.PASS


@dataclass(frozen=True)
class BatchValidationSummary:
    total_checks: int
    passed_checks: int
    failed_checks: int
    warning_checks: int

    @property
    def failed(self) -> bool:
        return self.failed_checks > 0


def pass_result(check_name: str, message: str = "passed", **details: object) -> ValidationResult:
    return ValidationResult(
        check_name=check_name,
        status=ValidationStatus.PASS,
        severity=ValidationSeverity.INFO,
        message=message,
        details=details,
    )


def fail_result(
    check_name: str,
    message: str,
    *,
    field_name: str | None = None,
    severity: ValidationSeverity = ValidationSeverity.ERROR,
    **details: object,
) -> ValidationResult:
    return ValidationResult(
        check_name=check_name,
        status=ValidationStatus.FAIL,
        severity=severity,
        message=message,
        field_name=field_name,
        details=details,
    )


def warn_result(check_name: str, message: str, **details: object) -> ValidationResult:
    return ValidationResult(
        check_name=check_name,
        status=ValidationStatus.WARN,
        severity=ValidationSeverity.WARN,
        message=message,
        details=details,
    )


def summarize_results(results: list[ValidationResult]) -> BatchValidationSummary:
    passed_checks = sum(1 for result in results if result.status == ValidationStatus.PASS)
    failed_checks = sum(1 for result in results if result.status == ValidationStatus.FAIL)
    warning_checks = sum(1 for result in results if result.status == ValidationStatus.WARN)
    return BatchValidationSummary(
        total_checks=len(results),
        passed_checks=passed_checks,
        failed_checks=failed_checks,
        warning_checks=warning_checks,
    )
