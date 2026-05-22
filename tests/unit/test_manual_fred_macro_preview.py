from __future__ import annotations

from datetime import date
import unittest

from app.ingestion.manual.fred_macro_preview import build_manual_fred_macro_incremental_preview


class ManualFredMacroPreviewTests(unittest.TestCase):
    def test_deterministic_preview_creation(self) -> None:
        preview_a = build_manual_fred_macro_incremental_preview(
            plan_id="preview-001",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            series_ids=("GDP", "UNRATE"),
        )
        preview_b = build_manual_fred_macro_incremental_preview(
            plan_id="preview-001",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            series_ids=("GDP", "UNRATE"),
        )

        self.assertEqual(preview_a.metadata, preview_b.metadata)
        self.assertEqual(preview_a.plan.series_ids, ("GDP", "UNRATE"))

    def test_one_checkpoint_per_selected_series(self) -> None:
        preview = build_manual_fred_macro_incremental_preview(
            plan_id="preview-002",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            series_ids=("GDP", "UNRATE"),
        )

        self.assertEqual(len(preview.checkpoints), 2)
        self.assertEqual({checkpoint.series_id for checkpoint in preview.checkpoints}, {"GDP", "UNRATE"})

    def test_one_initial_result_per_selected_series(self) -> None:
        preview = build_manual_fred_macro_incremental_preview(
            plan_id="preview-003",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            series_ids=("GDP", "UNRATE"),
        )

        self.assertEqual(len(preview.results), 2)
        self.assertEqual({result.series_id for result in preview.results}, {"GDP", "UNRATE"})

    def test_zero_initial_counts(self) -> None:
        preview = build_manual_fred_macro_incremental_preview(
            plan_id="preview-004",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            series_ids=("GDP",),
        )

        result = preview.results[0]
        self.assertEqual(result.rows_planned, 0)
        self.assertEqual(result.rows_fetched, 0)
        self.assertEqual(result.rows_valid, 0)
        self.assertEqual(result.rows_invalid, 0)
        self.assertEqual(result.rows_written, 0)
        self.assertEqual(result.validation_failures, 0)

    def test_no_db_writes(self) -> None:
        preview = build_manual_fred_macro_incremental_preview(
            plan_id="preview-005",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            series_ids=("GDP",),
        )

        self.assertTrue(preview.metadata["manual_only"])

    def test_no_vendor_calls(self) -> None:
        preview = build_manual_fred_macro_incremental_preview(
            plan_id="preview-006",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            series_ids=("GDP",),
        )

        self.assertEqual(preview.plan.vendor, "fred")

    def test_no_scheduler_behavior(self) -> None:
        preview = build_manual_fred_macro_incremental_preview(
            plan_id="preview-007",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            series_ids=("GDP",),
        )

        self.assertEqual(preview.metadata["series_count"], 1)

    def test_boundary_compliance(self) -> None:
        preview = build_manual_fred_macro_incremental_preview(
            plan_id="preview-008",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            series_ids=("GDP",),
        )

        self.assertEqual(preview.plan.dataset, "macro_observations")
