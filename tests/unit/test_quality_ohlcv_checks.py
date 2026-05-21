import unittest
from datetime import datetime

from app.models.normalized import NormalizedOHLCVRecord
from app.quality.ohlcv_checks import detect_duplicate_candles, validate_ohlcv_record


class OhlcvQualityTests(unittest.TestCase):
    def test_valid_ohlcv_passes(self) -> None:
        record = NormalizedOHLCVRecord(
            symbol="AAPL",
            symbol_id="sym-1",
            timestamp=datetime(2026, 1, 1, 14, 30),
            open=100.0,
            high=101.0,
            low=99.0,
            close=100.5,
            volume=123.0,
        )

        results = validate_ohlcv_record(record)
        self.assertTrue(all(result.passed for result in results))

    def test_invalid_price_relationships_fail(self) -> None:
        record = NormalizedOHLCVRecord(
            symbol="AAPL",
            symbol_id="sym-1",
            timestamp=datetime(2026, 1, 1, 14, 30),
            open=100.0,
            high=99.0,
            low=98.0,
            close=101.0,
            volume=123.0,
        )

        results = validate_ohlcv_record(record)
        self.assertTrue(any(result.check_name == "high_gte_open" and not result.passed for result in results))

    def test_duplicate_candle_detection(self) -> None:
        record_a = NormalizedOHLCVRecord(
            symbol="AAPL",
            symbol_id="sym-1",
            timestamp=datetime(2026, 1, 1, 14, 30),
            open=100.0,
            high=101.0,
            low=99.0,
            close=100.5,
            volume=123.0,
        )
        record_b = NormalizedOHLCVRecord(
            symbol="AAPL",
            symbol_id="sym-1",
            timestamp=datetime(2026, 1, 1, 14, 30),
            open=100.0,
            high=101.0,
            low=99.0,
            close=100.5,
            volume=123.0,
        )

        duplicates = detect_duplicate_candles([record_a, record_b])
        self.assertEqual(len(duplicates), 1)
