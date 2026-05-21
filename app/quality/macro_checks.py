from __future__ import annotations

from app.models.normalized import NormalizedMacroObservation
from app.quality.validators import ValidationResult, fail_result, pass_result


def validate_macro_observation(record: NormalizedMacroObservation) -> list[ValidationResult]:
    results: list[ValidationResult] = []

    results.append(
        pass_result("series_id_present")
        if record.symbol_id or record.symbol
        else fail_result("series_id_present", "series_id is required", field_name="symbol_id")
    )
    results.append(
        pass_result("timestamp_present")
        if record.timestamp is not None
        else fail_result("timestamp_present", "timestamp is required", field_name="timestamp")
    )
    results.append(
        pass_result("value_present")
        if record.value is not None
        else fail_result("value_present", "value is required", field_name="value")
    )
    if record.vendor is not None:
        results.append(
            pass_result("vendor_present")
            if record.vendor
            else fail_result("vendor_present", "vendor cannot be empty", field_name="vendor")
        )
    if record.source is not None:
        results.append(
            pass_result("source_present")
            if record.source
            else fail_result("source_present", "source cannot be empty", field_name="source")
        )

    return results
