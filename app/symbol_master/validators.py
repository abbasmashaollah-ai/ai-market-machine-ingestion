from __future__ import annotations

from app.models.normalized import NormalizedSymbolRecord
from app.quality.validators import ValidationResult, fail_result, pass_result


def validate_symbol_record(record: NormalizedSymbolRecord) -> list[ValidationResult]:
    results: list[ValidationResult] = []

    results.append(
        pass_result("symbol_present")
        if record.symbol
        else fail_result("symbol_present", "symbol is required", field_name="symbol")
    )
    if record.vendor is not None:
        results.append(
            pass_result("vendor_consistent")
            if record.vendor.strip()
            else fail_result("vendor_consistent", "vendor cannot be empty", field_name="vendor")
        )
    if record.source is not None:
        results.append(
            pass_result("source_consistent")
            if record.source.strip()
            else fail_result("source_consistent", "source cannot be empty", field_name="source")
        )
    if record.active is not None:
        results.append(
            pass_result("active_boolean")
            if isinstance(record.active, bool)
            else fail_result("active_boolean", "active must be boolean", field_name="active")
        )
    return results
