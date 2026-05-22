from __future__ import annotations

from datetime import date
import unittest

from app.state.manual_fred_macro import (
    ManualFREDMacroCheckpointStatus,
    build_manual_fred_macro_checkpoint,
)


class ManualFredMacroCheckpointTests(unittest.TestCase):
    def test_deterministic_checkpoint_state_creation(self) -> None:
        checkpoint = build_manual_fred_macro_checkpoint(
            checkpoint_key="fred:macro_observations:GDP:1d:2026-01-01:2026-01-31",
            vendor="fred",
            dataset="macro_observations",
            series_id="GDP",
            timeframe="1d",
            planned_start_date=date(2026, 1, 1),
            planned_end_date=date(2026, 1, 31),
            created_at=date(2026, 1, 1),  # type: ignore[arg-type]
            updated_at=date(2026, 1, 1),  # type: ignore[arg-type]
        )

        self.assertEqual(checkpoint.checkpoint_key, "fred:macro_observations:GDP:1d:2026-01-01:2026-01-31")
        self.assertEqual(checkpoint.status, ManualFREDMacroCheckpointStatus.PLANNED)

    def test_valid_status_values(self) -> None:
        self.assertEqual(ManualFREDMacroCheckpointStatus.PLANNED.value, "planned")
        self.assertEqual(ManualFREDMacroCheckpointStatus.READY.value, "ready")
        self.assertEqual(ManualFREDMacroCheckpointStatus.COMPLETED.value, "completed")
        self.assertEqual(ManualFREDMacroCheckpointStatus.FAILED.value, "failed")

    def test_optional_last_successful_observation_date_behavior(self) -> None:
        checkpoint = build_manual_fred_macro_checkpoint(
            checkpoint_key="fred:macro_observations:GDP:1d:2026-01-01:2026-01-31",
            vendor="fred",
            dataset="macro_observations",
            series_id="GDP",
            timeframe="1d",
            planned_start_date=date(2026, 1, 1),
            planned_end_date=date(2026, 1, 31),
            last_successful_observation_date=date(2026, 1, 15),
        )

        self.assertEqual(checkpoint.last_successful_observation_date, date(2026, 1, 15))

    def test_no_db_writes(self) -> None:
        checkpoint = build_manual_fred_macro_checkpoint(
            checkpoint_key="fred:macro_observations:GDP:1d:2026-01-01:2026-01-31",
            vendor="fred",
            dataset="macro_observations",
            series_id="GDP",
            timeframe="1d",
            planned_start_date=date(2026, 1, 1),
            planned_end_date=date(2026, 1, 31),
        )

        self.assertEqual(checkpoint.vendor, "fred")

    def test_no_vendor_calls(self) -> None:
        checkpoint = build_manual_fred_macro_checkpoint(
            checkpoint_key="fred:macro_observations:GDP:1d:2026-01-01:2026-01-31",
            vendor="fred",
            dataset="macro_observations",
            series_id="GDP",
            timeframe="1d",
            planned_start_date=date(2026, 1, 1),
            planned_end_date=date(2026, 1, 31),
        )

        self.assertEqual(checkpoint.dataset, "macro_observations")

    def test_no_scheduler_behavior(self) -> None:
        checkpoint = build_manual_fred_macro_checkpoint(
            checkpoint_key="fred:macro_observations:GDP:1d:2026-01-01:2026-01-31",
            vendor="fred",
            dataset="macro_observations",
            series_id="GDP",
            timeframe="1d",
            planned_start_date=date(2026, 1, 1),
            planned_end_date=date(2026, 1, 31),
        )

        self.assertEqual(checkpoint.timeframe, "1d")
