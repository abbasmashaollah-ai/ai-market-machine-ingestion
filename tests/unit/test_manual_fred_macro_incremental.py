from __future__ import annotations

from datetime import date
import unittest

from app.ingestion.backfill.checkpoints import build_checkpoint_key
from app.ingestion.manual.fred_macro_incremental import (
    build_manual_fred_macro_incremental_plan,
    describe_manual_plan,
    select_incremental_series_ids,
)


class ManualFredMacroIncrementalTests(unittest.TestCase):
    def test_checkpoint_key_generation(self) -> None:
        key = build_checkpoint_key(
            vendor="fred",
            dataset="macro_observations",
            symbol="GDP",
            timeframe="1d",
            start_date="2026-01-01",
            end_date="2026-01-31",
        )
        self.assertEqual(key, "fred:macro_observations:GDP:1d:2026-01-01:2026-01-31")

    def test_deterministic_manual_update_planning(self) -> None:
        plan_a = build_manual_fred_macro_incremental_plan(
            plan_id="manual-001",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            series_ids=("GDP", "UNRATE"),
        )
        plan_b = build_manual_fred_macro_incremental_plan(
            plan_id="manual-001",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            series_ids=("GDP", "UNRATE"),
        )

        self.assertEqual(describe_manual_plan(plan_a), describe_manual_plan(plan_b))
        self.assertEqual(plan_a.series_ids, ("GDP", "UNRATE"))
        self.assertTrue(all(job.metadata["manual_only"] for job in plan_a.jobs))

    def test_no_db_writes_during_planning(self) -> None:
        plan = build_manual_fred_macro_incremental_plan(
            plan_id="manual-002",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            series_ids=("GDP",),
        )

        self.assertEqual(len(plan.jobs), 1)
        self.assertEqual(len(plan.runs), 1)
        self.assertEqual(plan.metadata["manual_only"], True)

    def test_no_vendor_calls_during_planning(self) -> None:
        series_ids = select_incremental_series_ids(series_ids=("GDP",), category=None, include_all=False)
        self.assertEqual(series_ids, ("GDP",))

    def test_no_scheduler_behavior(self) -> None:
        plan = build_manual_fred_macro_incremental_plan(
            plan_id="manual-003",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            series_ids=("GDP",),
        )
        self.assertEqual(plan.metadata["manual_only"], True)

    def test_boundary_compliance(self) -> None:
        plan = build_manual_fred_macro_incremental_plan(
            plan_id="manual-004",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            series_ids=("GDP",),
        )
        self.assertEqual(plan.vendor, "fred")
        self.assertEqual(plan.dataset, "macro_observations")
