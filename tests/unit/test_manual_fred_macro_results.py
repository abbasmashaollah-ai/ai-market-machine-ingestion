from __future__ import annotations

from datetime import date
import unittest

from app.state.manual_fred_macro_results import (
    ManualFREDMacroRunStatus,
    build_manual_fred_macro_run_result,
)


class ManualFredMacroRunResultTests(unittest.TestCase):
    def test_deterministic_result_creation(self) -> None:
        result = build_manual_fred_macro_run_result(
            checkpoint_key="fred:macro_observations:GDP:1d:2026-01-01:2026-01-31",
            series_id="GDP",
            status=ManualFREDMacroRunStatus.SUCCESS,
            planned_start_date=date(2026, 1, 1),
            planned_end_date=date(2026, 1, 31),
            rows_planned=10,
            rows_fetched=10,
            rows_valid=9,
            rows_invalid=1,
            rows_written=9,
            validation_failures=1,
            error_message="sanitized failure",
        )

        self.assertEqual(result.checkpoint_key, "fred:macro_observations:GDP:1d:2026-01-01:2026-01-31")
        self.assertEqual(result.status, ManualFREDMacroRunStatus.SUCCESS)
        self.assertEqual(result.rows_planned, 10)

    def test_count_summary_behavior(self) -> None:
        result = build_manual_fred_macro_run_result(
            checkpoint_key="fred:macro_observations:GDP:1d:2026-01-01:2026-01-31",
            series_id="GDP",
            status=ManualFREDMacroRunStatus.PARTIAL,
            planned_start_date=date(2026, 1, 1),
            planned_end_date=date(2026, 1, 31),
            rows_planned=10,
            rows_fetched=8,
            rows_valid=7,
            rows_invalid=1,
            rows_written=7,
            validation_failures=1,
        )

        self.assertEqual(result.rows_fetched, 8)
        self.assertEqual(result.rows_written, 7)
        self.assertEqual(result.validation_failures, 1)

    def test_optional_sanitized_error_behavior(self) -> None:
        result = build_manual_fred_macro_run_result(
            checkpoint_key="fred:macro_observations:GDP:1d:2026-01-01:2026-01-31",
            series_id="GDP",
            status=ManualFREDMacroRunStatus.FAILED,
            planned_start_date=date(2026, 1, 1),
            planned_end_date=date(2026, 1, 31),
            rows_planned=10,
            rows_fetched=0,
            rows_valid=0,
            rows_invalid=0,
            rows_written=0,
            validation_failures=0,
            error_message="sanitized error",
        )

        self.assertEqual(result.error_message, "sanitized error")

    def test_no_db_writes(self) -> None:
        result = build_manual_fred_macro_run_result(
            checkpoint_key="fred:macro_observations:GDP:1d:2026-01-01:2026-01-31",
            series_id="GDP",
            status=ManualFREDMacroRunStatus.SKIPPED,
            planned_start_date=date(2026, 1, 1),
            planned_end_date=date(2026, 1, 31),
            rows_planned=0,
            rows_fetched=0,
            rows_valid=0,
            rows_invalid=0,
            rows_written=0,
            validation_failures=0,
        )

        self.assertEqual(result.rows_written, 0)

    def test_no_vendor_calls(self) -> None:
        result = build_manual_fred_macro_run_result(
            checkpoint_key="fred:macro_observations:GDP:1d:2026-01-01:2026-01-31",
            series_id="GDP",
            status=ManualFREDMacroRunStatus.PLANNED,
            planned_start_date=date(2026, 1, 1),
            planned_end_date=date(2026, 1, 31),
            rows_planned=0,
            rows_fetched=0,
            rows_valid=0,
            rows_invalid=0,
            rows_written=0,
            validation_failures=0,
        )

        self.assertEqual(result.series_id, "GDP")

    def test_no_scheduler_behavior(self) -> None:
        result = build_manual_fred_macro_run_result(
            checkpoint_key="fred:macro_observations:GDP:1d:2026-01-01:2026-01-31",
            series_id="GDP",
            status=ManualFREDMacroRunStatus.PLANNED,
            planned_start_date=date(2026, 1, 1),
            planned_end_date=date(2026, 1, 31),
            rows_planned=0,
            rows_fetched=0,
            rows_valid=0,
            rows_invalid=0,
            rows_written=0,
            validation_failures=0,
        )

        self.assertEqual(result.status, ManualFREDMacroRunStatus.PLANNED)
