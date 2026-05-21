import unittest
from datetime import date, datetime

from app.models.normalized import (
    NormalizedOHLCVRecord,
    NormalizedSymbolRecord,
)


class NormalizedModelTests(unittest.TestCase):
    def test_create_normalized_ohlcv_record(self) -> None:
        record = NormalizedOHLCVRecord(
            symbol="AAPL",
            symbol_id="sym-1",
            timestamp=datetime(2026, 1, 1, 14, 30),
            market_date=date(2026, 1, 1),
            open=100.0,
            high=101.0,
            low=99.5,
            close=100.5,
            volume=12345.0,
            vendor="polygon",
            source="equities",
            ingestion_run_id="run-1",
            normalization_version="v1",
            quality_status="pending",
        )

        self.assertEqual(record.symbol, "AAPL")
        self.assertEqual(record.symbol_id, "sym-1")
        self.assertEqual(record.timeframe, "1d")
        self.assertFalse(record.adjusted)
        self.assertEqual(record.close, 100.5)

    def test_adjusted_and_timeframe_defaults(self) -> None:
        record = NormalizedOHLCVRecord(
            symbol=None,
            symbol_id=None,
            timestamp=datetime(2026, 1, 1, 14, 30),
        )

        self.assertFalse(record.adjusted)
        self.assertEqual(record.timeframe, "1d")

    def test_symbol_record_shape(self) -> None:
        record = NormalizedSymbolRecord(
            symbol="AAPL",
            symbol_id="sym-1",
            vendor="polygon",
            source="equities",
            ingestion_run_id="run-1",
            normalization_version="v1",
            quality_status="pending",
            asset_class="equity",
            exchange="NASDAQ",
            active=True,
        )

        self.assertEqual(record.symbol, "AAPL")
        self.assertEqual(record.asset_class, "equity")
        self.assertTrue(record.active)
