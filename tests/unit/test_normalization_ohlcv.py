import unittest
from datetime import date

from app.normalization.ohlcv import normalize_ohlcv


class OhlcvNormalizationTests(unittest.TestCase):
    def test_normalize_ohlcv_dict(self) -> None:
        record = normalize_ohlcv(
            {
                "symbol": "AAPL",
                "symbol_id": "sym-1",
                "timestamp": "2026-01-02T10:00:00-08:00",
                "market_date": date(2026, 1, 2),
                "open": "100.0",
                "high": "101.0",
                "low": "99.0",
                "close": "100.5",
                "volume": "12345",
                "vendor": "polygon",
                "source": "equities",
                "ingestion_run_id": "run-1",
                "normalization_version": "v1",
                "quality_status": "pending",
            }
        )

        self.assertEqual(record.symbol, "AAPL")
        self.assertEqual(record.timeframe, "1d")
        self.assertFalse(record.adjusted)
        self.assertEqual(record.timestamp.hour, 18)

    def test_missing_timestamp_raises(self) -> None:
        with self.assertRaises(ValueError):
            normalize_ohlcv({})
