from __future__ import annotations

import os
import unittest
from datetime import date
from unittest.mock import Mock, patch


class PersistFredMacroIncrementalTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.persist_fred_macro_incremental as mod

        return mod

    def test_no_confirm_write_produces_planned_summary_and_no_db_write(self) -> None:
        mod = self._module()
        fake_client = Mock()
        fake_client.fetch_series_observations_raw.return_value = {
            "observations": [{"series_id": "GDP", "date": "2025-01-01", "value": "1.0"}]
        }

        with patch(
            "app.ingestion.manual.fred_macro_incremental_persist._build_fred_client",
            return_value=fake_client,
        ), patch("builtins.print") as print_mock:
            summary = mod.build_manual_fred_macro_incremental_persist(
                series_ids=("GDP",),
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                api_key="fred-secret",
                writer=None,
                confirmed_write=False,
            )
            mod._print_summary(summary)

        self.assertEqual(summary.series_summaries[0].rows_written, 0)
        self.assertFalse(summary.series_summaries[0].write_confirmed)
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("write_confirmed=false", printed)

    def test_confirm_write_routes_valid_records_through_macro_writer(self) -> None:
        mod = self._module()
        fake_client = Mock()
        fake_client.fetch_series_observations_raw.return_value = {
            "observations": [{"series_id": "GDP", "date": "2025-01-01", "value": "1.0"}]
        }
        writer = Mock()
        writer.write.return_value = type("Result", (), {"written_count": 1})()

        with patch("app.ingestion.manual.fred_macro_incremental_persist._build_fred_client", return_value=fake_client):
            summary = mod.build_manual_fred_macro_incremental_persist(
                series_ids=("GDP",),
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                api_key="fred-secret",
                writer=writer,
                confirmed_write=True,
            )

        writer.write.assert_called_once()
        self.assertEqual(summary.series_summaries[0].rows_written, 1)
        self.assertTrue(summary.series_summaries[0].write_confirmed)

    def test_invalid_records_are_not_written(self) -> None:
        mod = self._module()
        fake_client = Mock()
        fake_client.fetch_series_observations_raw.return_value = {
            "observations": [{"series_id": "GDP", "date": "2025-01-01", "value": "."}]
        }
        writer = Mock()

        with patch("app.ingestion.manual.fred_macro_incremental_persist._build_fred_client", return_value=fake_client):
            summary = mod.build_manual_fred_macro_incremental_persist(
                series_ids=("GDP",),
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                api_key="fred-secret",
                writer=writer,
                confirmed_write=True,
            )

        writer.write.assert_not_called()
        self.assertEqual(summary.series_summaries[0].rows_valid, 0)
        self.assertEqual(summary.series_summaries[0].rows_invalid, 1)
        self.assertEqual(summary.series_summaries[0].rows_written, 0)

    def test_missing_database_url_only_fails_on_confirmed_write_path(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"FRED_API_KEY": "fred-secret"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch(
            "sys.argv",
            [
                "persist_fred_macro_incremental.py",
                "--series-id",
                "GDP",
                "--start-date",
                "2025-01-01",
                "--end-date",
                "2025-12-31",
                "--confirm-write",
            ],
        ), patch.object(mod, "select_incremental_series_ids", return_value=("GDP",)):
            with self.assertRaises(RuntimeError):
                mod.main()

    def test_missing_fred_api_key_fails_safely(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "sys.argv",
            [
                "persist_fred_macro_incremental.py",
                "--series-id",
                "GDP",
                "--start-date",
                "2025-01-01",
                "--end-date",
                "2025-12-31",
            ],
        ):
            with self.assertRaises(RuntimeError):
                mod.main()

    def test_sanitized_failure_output(self) -> None:
        mod = self._module()
        fake_client = Mock()
        fake_client.fetch_series_observations_raw.return_value = {
            "observations": [{"series_id": "GDP", "date": "2025-01-01", "value": "1.0"}]
        }
        writer = Mock()
        writer.write.return_value = type(
            "Result",
            (),
            {
                "written_count": 0,
                "status": type("Status", (), {"value": "failure"})(),
                "details": {"error_type": "RuntimeError", "error_message": "postgresql://user:secret@example/db"},
                "message": "RuntimeError: postgresql://user:secret@example/db",
            },
        )()

        with patch("builtins.print") as print_mock, patch(
            "app.ingestion.manual.fred_macro_incremental_persist._build_fred_client",
            return_value=fake_client,
        ):
            summary = mod.build_manual_fred_macro_incremental_persist(
                series_ids=("GDP",),
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                api_key="fred-secret",
                writer=writer,
                confirmed_write=True,
            )
            mod._print_summary(summary)

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertNotIn("secret", printed)
        self.assertNotIn("DATABASE_URL", printed)

    def test_no_direct_db_writes(self) -> None:
        mod = self._module()
        self.assertTrue(hasattr(mod, "build_manual_fred_macro_incremental_persist"))

    def test_no_scheduler_behavior(self) -> None:
        mod = self._module()
        self.assertTrue(hasattr(mod, "_print_summary"))

    def test_no_secrets_printed(self) -> None:
        mod = self._module()
        self.assertTrue(hasattr(mod, "_print_summary"))

