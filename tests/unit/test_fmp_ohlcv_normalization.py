import unittest

from app.ingestion.ohlcv.normalization import normalize_fmp_ohlcv_record, normalize_fmp_ohlcv_records


class FmpOhlcvNormalizationTests(unittest.TestCase):
    def test_normalize_single_record(self) -> None:
        record = normalize_fmp_ohlcv_record(
            {
                "date": "2026-01-02",
                "open": "100.0",
                "high": "101.0",
                "low": "99.0",
                "close": "100.5",
                "volume": "12345",
                "adjClose": "100.25",
            },
            symbol="AAPL",
        )

        self.assertEqual(record.symbol, "AAPL")
        self.assertEqual(record.symbol_id, "AAPL")
        self.assertEqual(record.timeframe, "1d")
        self.assertEqual(record.vendor, "fmp")
        self.assertEqual(record.source, "fmp_historical_price_full")
        self.assertTrue(record.adjusted)
        self.assertEqual(record.timestamp.year, 2026)
        self.assertEqual(record.market_date.isoformat(), "2026-01-02")

    def test_normalize_records(self) -> None:
        records = normalize_fmp_ohlcv_records(
            [
                {"date": "2026-01-02", "open": 1, "high": 2, "low": 0.5, "close": 1.5, "volume": 10},
                {"date": "2026-01-03", "open": 2, "high": 3, "low": 1.5, "close": 2.5, "volume": 20},
            ],
            symbol="AAPL",
        )

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].symbol, "AAPL")
        self.assertEqual(records[1].market_date.isoformat(), "2026-01-03")

    def test_missing_required_fields_raise(self) -> None:
        with self.assertRaises(ValueError):
            normalize_fmp_ohlcv_record({"date": "2026-01-02"}, symbol=None)
