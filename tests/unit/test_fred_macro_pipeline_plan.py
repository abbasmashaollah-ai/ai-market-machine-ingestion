import unittest
from datetime import date

from app.ingestion.pipelines.fred_macro import FredMacroPipelineRequest, plan_fred_macro_fetch_tasks


class FredMacroPipelinePlanTests(unittest.TestCase):
    def test_request_construction(self) -> None:
        request = FredMacroPipelineRequest(
            series_ids=("GDP", "CPIAUCSL"),
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
        )
        self.assertTrue(request.dry_run)
        self.assertEqual(request.series_ids, ("GDP", "CPIAUCSL"))

    def test_selected_series_ids_planning(self) -> None:
        request = FredMacroPipelineRequest(
            series_ids=("GDP", "CPIAUCSL"),
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
        )
        tasks = plan_fred_macro_fetch_tasks(request)
        self.assertEqual([task.series_id for task in tasks], ["GDP", "CPIAUCSL"])

    def test_category_planning(self) -> None:
        request = FredMacroPipelineRequest(
            series_ids=("GDP", "CPIAUCSL", "UNRATE"),
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            category="inflation",
        )
        tasks = plan_fred_macro_fetch_tasks(request)
        self.assertEqual([task.series_id for task in tasks], ["CPIAUCSL"])
        self.assertEqual(tasks[0].category, "inflation")

    def test_priority_planning(self) -> None:
        request = FredMacroPipelineRequest(
            series_ids=("GDP", "CPIAUCSL", "UNRATE"),
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            priority=1,
        )
        tasks = plan_fred_macro_fetch_tasks(request)
        self.assertEqual([task.series_id for task in tasks], ["GDP", "CPIAUCSL", "UNRATE"])

    def test_unknown_series_validation(self) -> None:
        request = FredMacroPipelineRequest(
            series_ids=("UNKNOWN",),
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
        )
        with self.assertRaises(ValueError):
            plan_fred_macro_fetch_tasks(request)

    def test_no_live_calls(self) -> None:
        request = FredMacroPipelineRequest(
            series_ids=("GDP",),
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
        )
        tasks = plan_fred_macro_fetch_tasks(request)
        self.assertEqual(tasks[0].vendor, "fred")
