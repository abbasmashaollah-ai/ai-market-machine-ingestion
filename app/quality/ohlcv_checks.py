from __future__ import annotations

from collections import Counter

from app.models.normalized import NormalizedOHLCVRecord
from app.quality.validators import ValidationResult, fail_result, pass_result


def validate_ohlcv_record(record: NormalizedOHLCVRecord) -> list[ValidationResult]:
    results: list[ValidationResult] = []

    results.append(
        pass_result("timestamp_present")
        if record.timestamp is not None
        else fail_result("timestamp_present", "timestamp is required", field_name="timestamp")
    )
    results.append(
        pass_result("symbol_present")
        if record.symbol or record.symbol_id
        else fail_result("symbol_present", "symbol or symbol_id is required", field_name="symbol")
    )
    results.append(
        pass_result("timeframe_present")
        if record.timeframe
        else fail_result("timeframe_present", "timeframe is required", field_name="timeframe")
    )

    price_fields = {
        "open": record.open,
        "high": record.high,
        "low": record.low,
        "close": record.close,
    }
    for field_name, value in price_fields.items():
        results.append(
            pass_result(f"{field_name}_present")
            if value is not None
            else fail_result(f"{field_name}_present", f"{field_name} is required", field_name=field_name)
        )

    if record.high is not None and record.low is not None:
        results.append(
            pass_result("high_gte_low")
            if record.high >= record.low
            else fail_result("high_gte_low", "high must be greater than or equal to low", field_name="high")
        )
    if record.high is not None and record.open is not None:
        results.append(
            pass_result("high_gte_open")
            if record.high >= record.open
            else fail_result("high_gte_open", "high must be greater than or equal to open", field_name="high")
        )
    if record.high is not None and record.close is not None:
        results.append(
            pass_result("high_gte_close")
            if record.high >= record.close
            else fail_result("high_gte_close", "high must be greater than or equal to close", field_name="high")
        )
    if record.low is not None and record.open is not None:
        results.append(
            pass_result("low_lte_open")
            if record.low <= record.open
            else fail_result("low_lte_open", "low must be less than or equal to open", field_name="low")
        )
    if record.low is not None and record.close is not None:
        results.append(
            pass_result("low_lte_close")
            if record.low <= record.close
            else fail_result("low_lte_close", "low must be less than or equal to close", field_name="low")
        )

    if record.volume is not None:
        results.append(
            pass_result("volume_non_negative")
            if record.volume >= 0
            else fail_result("volume_non_negative", "volume must be non-negative", field_name="volume")
        )

    results.append(
        pass_result("adjusted_boolean")
        if isinstance(record.adjusted, bool)
        else fail_result("adjusted_boolean", "adjusted must be boolean", field_name="adjusted")
    )

    return results


def detect_duplicate_candles(records: list[NormalizedOHLCVRecord]) -> list[ValidationResult]:
    keys = [
        (record.symbol_id or record.symbol, record.timestamp, record.timeframe, record.adjusted)
        for record in records
    ]
    counts = Counter(keys)
    duplicates = [
        fail_result(
            "duplicate_candle",
            "duplicate candle detected",
            field_name="symbol_id/symbol",
            key=key,
            count=count,
        )
        for key, count in counts.items()
        if count > 1
    ]
    return duplicates
