import unittest
from datetime import date, time

from app.ingestion.backfill.checkpoints import build_checkpoint_key
from app.ingestion.backfill.planner import BackfillRequest, DateChunk, split_date_range_into_chunks
from app.ingestion.backfill.orchestrator import BackfillOrchestrator
from app.ingestion.backfill.job_runner import BackfillJobRunner
from app.ingestion.daily.market_calendar import is_market_day, is_weekend
from app.ingestion.daily.scheduler import DailyScheduleConfig
from app.ingestion.daily.updater import DailyUpdateRequest, DailyUpdater


class IngestionPlanningTests(unittest.TestCase):
    def test_date_chunking(self) -> None:
        chunks = split_date_range_into_chunks(date(2026, 1, 1), date(2026, 1, 5), max_days_per_chunk=2)
        self.assertEqual(chunks, [
            DateChunk(start_date=date(2026, 1, 1), end_date=date(2026, 1, 2)),
            DateChunk(start_date=date(2026, 1, 3), end_date=date(2026, 1, 4)),
            DateChunk(start_date=date(2026, 1, 5), end_date=date(2026, 1, 5)),
        ])

    def test_invalid_date_ranges(self) -> None:
        with self.assertRaises(ValueError):
            split_date_range_into_chunks(date(2026, 1, 2), date(2026, 1, 1), max_days_per_chunk=2)

    def test_checkpoint_key_generation(self) -> None:
        key = build_checkpoint_key(
            vendor="polygon",
            dataset="ohlcv",
            symbol="AAPL",
            timeframe="1d",
            start_date="2026-01-01",
            end_date="2026-01-31",
        )
        self.assertEqual(key, "polygon:ohlcv:AAPL:1d:2026-01-01:2026-01-31")

    def test_weekend_market_calendar_helper(self) -> None:
        self.assertTrue(is_weekend(date(2026, 1, 3)))
        self.assertTrue(is_market_day(date(2026, 1, 5)))

    def test_daily_update_request_shape(self) -> None:
        request = DailyUpdateRequest(vendor="polygon", dataset="ohlcv", trading_date=date(2026, 1, 5))
        self.assertEqual(request.vendor, "polygon")
        self.assertEqual(request.metadata, {})

    def test_placeholder_boundaries(self) -> None:
        self.assertTrue(issubclass(BackfillOrchestrator, object))
        self.assertTrue(issubclass(BackfillJobRunner, object))
        self.assertTrue(issubclass(DailyUpdater, object))
