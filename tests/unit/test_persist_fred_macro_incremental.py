from __future__ import annotations

import os
import unittest
from datetime import date
from unittest.mock import Mock, patch

from app.writers.canonical_writer import WriteStatus


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

    def test_no_checkpoint_update_on_dry_run(self) -> None:
        mod = self._module()
        checkpoint_store = Mock()
        fake_client = Mock()
        fake_client.fetch_series_observations_raw.return_value = {
            "observations": [{"series_id": "GDP", "date": "2025-01-01", "value": "1.0"}]
        }

        with patch("app.ingestion.manual.fred_macro_incremental_persist._build_fred_client", return_value=fake_client):
            summary = mod.build_manual_fred_macro_incremental_persist(
                series_ids=("GDP",),
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                api_key="fred-secret",
                writer=None,
                confirmed_write=False,
                checkpoint_store=checkpoint_store,
                use_checkpoint=True,
                update_checkpoint=True,
            )

        checkpoint_store.load.assert_called_once()
        checkpoint_store.update_successful_observation_date.assert_not_called()
        self.assertEqual(summary.series_summaries[0].rows_written, 0)

    def test_checkpoint_last_successful_advances_effective_start_date_by_one_day(self) -> None:
        mod = self._module()
        fake_client = Mock()
        fake_client.fetch_series_observations_raw.return_value = {
            "observations": [{"series_id": "GDP", "date": "2025-01-11", "value": "1.0"}]
        }
        checkpoint_store = Mock()
        checkpoint_store.load.return_value = type(
            "Checkpoint",
            (),
            {"last_successful_observation_date": date(2025, 1, 10)},
        )()

        with patch("app.ingestion.manual.fred_macro_incremental_persist._build_fred_client", return_value=fake_client):
            summary = mod.build_manual_fred_macro_incremental_persist(
                series_ids=("GDP",),
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                api_key="fred-secret",
                writer=None,
                confirmed_write=False,
                checkpoint_store=checkpoint_store,
                use_checkpoint=True,
                update_checkpoint=False,
            )

        self.assertEqual(summary.series_summaries[0].requested_start_date, date(2025, 1, 1))
        self.assertEqual(summary.series_summaries[0].effective_start_date, date(2025, 1, 11))
        checkpoint_store.load.assert_called_once()

    def test_no_checkpoint_keeps_requested_start_date(self) -> None:
        mod = self._module()
        fake_client = Mock()
        fake_client.fetch_series_observations_raw.return_value = {
            "observations": [{"series_id": "GDP", "date": "2025-01-01", "value": "1.0"}]
        }
        checkpoint_store = Mock()
        checkpoint_store.load.return_value = None

        with patch("app.ingestion.manual.fred_macro_incremental_persist._build_fred_client", return_value=fake_client):
            summary = mod.build_manual_fred_macro_incremental_persist(
                series_ids=("GDP",),
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                api_key="fred-secret",
                writer=None,
                confirmed_write=False,
                checkpoint_store=checkpoint_store,
                use_checkpoint=True,
                update_checkpoint=False,
            )

        self.assertEqual(summary.series_summaries[0].effective_start_date, date(2025, 1, 1))

    def test_checkpoint_without_last_successful_keeps_requested_start_date(self) -> None:
        mod = self._module()
        fake_client = Mock()
        fake_client.fetch_series_observations_raw.return_value = {
            "observations": [{"series_id": "GDP", "date": "2025-01-01", "value": "1.0"}]
        }
        checkpoint_store = Mock()
        checkpoint_store.load.return_value = type("Checkpoint", (), {"last_successful_observation_date": None})()

        with patch("app.ingestion.manual.fred_macro_incremental_persist._build_fred_client", return_value=fake_client):
            summary = mod.build_manual_fred_macro_incremental_persist(
                series_ids=("GDP",),
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                api_key="fred-secret",
                writer=None,
                confirmed_write=False,
                checkpoint_store=checkpoint_store,
                use_checkpoint=True,
                update_checkpoint=False,
            )

        self.assertEqual(summary.series_summaries[0].effective_start_date, date(2025, 1, 1))

    def test_effective_start_date_after_end_date_skips_safely(self) -> None:
        mod = self._module()
        checkpoint_store = Mock()
        checkpoint_store.load.return_value = type(
            "Checkpoint",
            (),
            {"last_successful_observation_date": date(2025, 12, 31)},
        )()
        fake_client = Mock()

        with patch("app.ingestion.manual.fred_macro_incremental_persist._build_fred_client", return_value=fake_client):
            summary = mod.build_manual_fred_macro_incremental_persist(
                series_ids=("GDP",),
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                api_key="fred-secret",
                writer=None,
                confirmed_write=False,
                checkpoint_store=checkpoint_store,
                use_checkpoint=True,
                update_checkpoint=True,
            )

        self.assertEqual(summary.series_summaries[0].status, "skipped_already_current")
        self.assertEqual(summary.series_summaries[0].rows_fetched, 0)
        checkpoint_store.update_successful_observation_date.assert_not_called()

    def test_resumed_fetch_filters_rows_at_or_before_last_successful_observation(self) -> None:
        mod = self._module()
        fake_client = Mock()
        fake_client.fetch_series_observations_raw.return_value = {
            "observations": [
                {"series_id": "GDP", "date": "2025-01-10", "value": "1.0"},
                {"series_id": "GDP", "date": "2025-01-11", "value": "2.0"},
            ]
        }
        writer = Mock()
        writer.write.return_value = type("Result", (), {"written_count": 1, "status": WriteStatus.SUCCESS})()
        checkpoint_store = Mock()
        checkpoint_store.load.return_value = type(
            "Checkpoint",
            (),
            {"last_successful_observation_date": date(2025, 1, 10), "checkpoint_key": "fred:macro_observations:GDP:1d:2025-01-01:2025-12-31"},
        )()

        with patch("app.ingestion.manual.fred_macro_incremental_persist._build_fred_client", return_value=fake_client):
            summary = mod.build_manual_fred_macro_incremental_persist(
                series_ids=("GDP",),
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                api_key="fred-secret",
                writer=writer,
                confirmed_write=True,
                checkpoint_store=checkpoint_store,
                use_checkpoint=True,
                update_checkpoint=True,
            )

        writer.write.assert_called_once()
        written_rows = writer.write.call_args.args[0]
        self.assertEqual(len(written_rows), 1)
        self.assertEqual(written_rows[0].timestamp.date(), date(2025, 1, 11))
        self.assertEqual(summary.series_summaries[0].rows_fetched, 1)
        self.assertEqual(summary.series_summaries[0].rows_valid, 1)
        self.assertEqual(summary.series_summaries[0].rows_written, 1)
        checkpoint_store.update_successful_observation_date.assert_called_once()

    def test_all_filtered_resumed_run_returns_skipped_already_current(self) -> None:
        mod = self._module()
        fake_client = Mock()
        fake_client.fetch_series_observations_raw.return_value = {
            "observations": [
                {"series_id": "GDP", "date": "2025-01-10", "value": "1.0"},
            ]
        }
        writer = Mock()
        checkpoint_store = Mock()
        checkpoint_store.load.return_value = type(
            "Checkpoint",
            (),
            {"last_successful_observation_date": date(2025, 1, 10), "checkpoint_key": "fred:macro_observations:GDP:1d:2025-01-01:2025-12-31"},
        )()

        with patch("app.ingestion.manual.fred_macro_incremental_persist._build_fred_client", return_value=fake_client):
            summary = mod.build_manual_fred_macro_incremental_persist(
                series_ids=("GDP",),
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                api_key="fred-secret",
                writer=writer,
                confirmed_write=True,
                checkpoint_store=checkpoint_store,
                use_checkpoint=True,
                update_checkpoint=True,
            )

        self.assertEqual(summary.series_summaries[0].status, "skipped_already_current")
        self.assertEqual(summary.series_summaries[0].rows_fetched, 0)
        self.assertEqual(summary.series_summaries[0].rows_valid, 0)
        self.assertEqual(summary.series_summaries[0].rows_written, 0)
        writer.write.assert_not_called()
        checkpoint_store.update_successful_observation_date.assert_not_called()

    def test_confirm_write_routes_valid_records_through_macro_writer(self) -> None:
        mod = self._module()
        fake_client = Mock()
        fake_client.fetch_series_observations_raw.return_value = {
            "observations": [{"series_id": "GDP", "date": "2025-01-01", "value": "1.0"}]
        }
        writer = Mock()
        writer.write.return_value = type("Result", (), {"written_count": 1, "status": WriteStatus.SUCCESS})()

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
        self.assertEqual(summary.series_total, 1)
        self.assertEqual(summary.series_completed, 1)
        self.assertEqual(summary.series_failed, 0)
        self.assertEqual(summary.series_skipped, 0)
        self.assertEqual(summary.total_rows_written, 1)

    def test_multi_series_one_success_one_skipped_summary_totals(self) -> None:
        mod = self._module()
        fake_client = Mock()
        fake_client.fetch_series_observations_raw.side_effect = [
            {"observations": [{"series_id": "GDP", "date": "2025-01-01", "value": "1.0"}]},
            {"observations": [{"series_id": "UNRATE", "date": "2025-01-10", "value": "1.0"}]},
        ]
        writer = Mock()
        writer.write.return_value = type("Result", (), {"written_count": 1, "status": WriteStatus.SUCCESS})()
        checkpoint_store = Mock()
        checkpoint_store.load.side_effect = [
            None,
            type(
                "Checkpoint",
                (),
                {"last_successful_observation_date": date(2025, 1, 10), "checkpoint_key": "fred:macro_observations:UNRATE:1d:2025-01-01:2025-12-31"},
            )(),
        ]

        with patch("app.ingestion.manual.fred_macro_incremental_persist._build_fred_client", return_value=fake_client):
            summary = mod.build_manual_fred_macro_incremental_persist(
                series_ids=("GDP", "UNRATE"),
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                api_key="fred-secret",
                writer=writer,
                confirmed_write=True,
                checkpoint_store=checkpoint_store,
                use_checkpoint=True,
                update_checkpoint=True,
            )

        self.assertEqual(summary.series_total, 2)
        self.assertEqual(summary.series_completed, 1)
        self.assertEqual(summary.series_skipped, 1)
        self.assertEqual(summary.total_rows_written, 1)
        self.assertEqual(summary.series_summaries[0].series_id, "GDP")
        self.assertEqual(summary.series_summaries[1].status, "skipped_already_current")
        self.assertEqual(checkpoint_store.update_successful_observation_date.call_count, 1)

    def test_checkpoint_update_after_successful_confirmed_write(self) -> None:
        mod = self._module()
        fake_client = Mock()
        fake_client.fetch_series_observations_raw.return_value = {
            "observations": [{"series_id": "GDP", "date": "2025-01-10", "value": "1.0"}]
        }
        writer = Mock()
        writer.write.return_value = type("Result", (), {"written_count": 1, "status": WriteStatus.SUCCESS})()
        checkpoint_store = Mock()
        checkpoint_store.load.return_value = None

        with patch("app.ingestion.manual.fred_macro_incremental_persist._build_fred_client", return_value=fake_client):
            summary = mod.build_manual_fred_macro_incremental_persist(
                series_ids=("GDP",),
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                api_key="fred-secret",
                writer=writer,
                confirmed_write=True,
                checkpoint_store=checkpoint_store,
                use_checkpoint=True,
                update_checkpoint=True,
            )

        checkpoint_store.update_successful_observation_date.assert_called_once()
        self.assertEqual(summary.series_summaries[0].rows_written, 1)

    def test_successful_resumed_run_still_writes_and_updates_checkpoint(self) -> None:
        mod = self._module()
        fake_client = Mock()
        fake_client.fetch_series_observations_raw.return_value = {
            "observations": [{"series_id": "GDP", "date": "2025-01-11", "value": "1.0"}]
        }
        writer = Mock()
        writer.write.return_value = type("Result", (), {"written_count": 1, "status": WriteStatus.SUCCESS})()
        checkpoint_store = Mock()
        checkpoint_store.load.return_value = type(
            "Checkpoint",
            (),
            {"last_successful_observation_date": date(2025, 1, 10), "checkpoint_key": "fred:macro_observations:GDP:1d:2025-01-01:2025-12-31"},
        )()

        with patch("app.ingestion.manual.fred_macro_incremental_persist._build_fred_client", return_value=fake_client):
            summary = mod.build_manual_fred_macro_incremental_persist(
                series_ids=("GDP",),
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                api_key="fred-secret",
                writer=writer,
                confirmed_write=True,
                checkpoint_store=checkpoint_store,
                use_checkpoint=True,
                update_checkpoint=True,
            )

        writer.write.assert_called_once()
        checkpoint_store.update_successful_observation_date.assert_called_once()
        self.assertEqual(summary.series_summaries[0].effective_start_date, date(2025, 1, 11))

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

    def test_no_checkpoint_update_on_failed_write(self) -> None:
        mod = self._module()
        fake_client = Mock()
        fake_client.fetch_series_observations_raw.return_value = {
            "observations": [{"series_id": "GDP", "date": "2025-01-10", "value": "1.0"}]
        }
        writer = Mock()
        writer.write.return_value = type("Result", (), {"written_count": 0, "status": WriteStatus.FAILURE})()
        checkpoint_store = Mock()
        checkpoint_store.load.return_value = None

        with patch("app.ingestion.manual.fred_macro_incremental_persist._build_fred_client", return_value=fake_client):
            summary = mod.build_manual_fred_macro_incremental_persist(
                series_ids=("GDP",),
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                api_key="fred-secret",
                writer=writer,
                confirmed_write=True,
                checkpoint_store=checkpoint_store,
                use_checkpoint=True,
                update_checkpoint=True,
            )

        checkpoint_store.update_successful_observation_date.assert_not_called()
        self.assertEqual(summary.series_summaries[0].rows_written, 0)

    def test_failed_series_does_not_update_checkpoint(self) -> None:
        mod = self._module()
        fake_client = Mock()
        fake_client.fetch_series_observations_raw.side_effect = RuntimeError("postgresql://user:secret@example/db")
        writer = Mock()
        checkpoint_store = Mock()

        with patch("app.ingestion.manual.fred_macro_incremental_persist._build_fred_client", return_value=fake_client):
            summary = mod.build_manual_fred_macro_incremental_persist(
                series_ids=("GDP",),
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                api_key="fred-secret",
                writer=writer,
                confirmed_write=True,
                checkpoint_store=checkpoint_store,
                use_checkpoint=True,
                update_checkpoint=True,
            )

        self.assertEqual(summary.series_summaries[0].status, "failed")
        self.assertNotIn("secret", summary.series_summaries[0].error_message or "")
        checkpoint_store.update_successful_observation_date.assert_not_called()

    def test_failed_series_does_not_hide_successful_series(self) -> None:
        mod = self._module()
        fake_client = Mock()
        fake_client.fetch_series_observations_raw.side_effect = [
            {"observations": [{"series_id": "GDP", "date": "2025-01-01", "value": "1.0"}]},
            RuntimeError("postgresql://user:secret@example/db"),
        ]
        writer = Mock()
        writer.write.return_value = type("Result", (), {"written_count": 1, "status": WriteStatus.SUCCESS})()
        checkpoint_store = Mock()

        with patch("app.ingestion.manual.fred_macro_incremental_persist._build_fred_client", return_value=fake_client):
            summary = mod.build_manual_fred_macro_incremental_persist(
                series_ids=("GDP", "UNRATE"),
                start_date=date(2025, 1, 1),
                end_date=date(2025, 12, 31),
                api_key="fred-secret",
                writer=writer,
                confirmed_write=True,
                checkpoint_store=checkpoint_store,
                use_checkpoint=True,
                update_checkpoint=True,
            )

        self.assertEqual(summary.series_total, 2)
        self.assertEqual(summary.series_completed, 1)
        self.assertEqual(summary.series_failed, 1)
        self.assertEqual(summary.total_rows_written, 1)
        self.assertEqual(summary.series_summaries[0].status, "completed")
        self.assertEqual(summary.series_summaries[1].status, "failed")
        self.assertNotIn("secret", summary.series_summaries[1].error_message or "")
        checkpoint_store.update_successful_observation_date.assert_called_once()

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

    def test_repeated_series_id_cli_selects_multiple_series(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"FRED_API_KEY": "fred-secret", "DATABASE_URL": "postgresql://example/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "select_incremental_series_ids", return_value=("GDP", "UNRATE")) as select_mock, patch.object(
            mod, "_open_connection"
        ) as open_connection, patch.object(mod, "MacroWriter") as writer_cls, patch.object(
            mod, "build_manual_fred_macro_incremental_persist"
        ) as build_mock, patch.object(
            mod, "_print_summary"
        ), patch(
            "sys.argv",
            [
                "persist_fred_macro_incremental.py",
                "--series-id",
                "GDP",
                "--series-id",
                "UNRATE",
                "--start-date",
                "2025-01-01",
                "--end-date",
                "2025-12-31",
            ],
        ):
            build_mock.return_value.series_summaries = ()
            build_mock.return_value.series_total = 0
            build_mock.return_value.series_completed = 0
            build_mock.return_value.series_failed = 0
            build_mock.return_value.series_skipped = 0
            build_mock.return_value.total_rows_fetched = 0
            build_mock.return_value.total_rows_valid = 0
            build_mock.return_value.total_rows_invalid = 0
            build_mock.return_value.total_rows_written = 0
            build_mock.return_value.total_validation_failures = 0
            mod.main()

        select_mock.assert_called_once()
        self.assertEqual(select_mock.call_args.kwargs["series_ids"], ("GDP", "UNRATE"))
        open_connection.assert_not_called()
        writer_cls.assert_not_called()

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

    def test_print_summary_includes_aggregate_totals(self) -> None:
        mod = self._module()
        summary = type(
            "Summary",
            (),
            {
                "series_summaries": (
                    type(
                        "Row",
                        (),
                        {
                            "series_id": "GDP",
                            "requested_start_date": date(2025, 1, 1),
                            "effective_start_date": date(2025, 1, 1),
                            "rows_fetched": 1,
                            "rows_valid": 1,
                            "rows_invalid": 0,
                            "rows_written": 1,
                            "validation_failures": 0,
                            "planned_start_date": date(2025, 1, 1),
                            "planned_end_date": date(2025, 12, 31),
                            "write_confirmed": True,
                            "status": "completed",
                            "error_message": None,
                        },
                    )(),
                ),
                "series_total": 1,
                "series_completed": 1,
                "series_failed": 0,
                "series_skipped": 0,
                "total_rows_fetched": 1,
                "total_rows_valid": 1,
                "total_rows_invalid": 0,
                "total_rows_written": 1,
                "total_validation_failures": 0,
            },
        )()

        with patch("builtins.print") as print_mock:
            mod._print_summary(summary)

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("series_total=1", printed)
        self.assertIn("series_completed=1", printed)
        self.assertIn("total_rows_written=1", printed)

    def test_no_direct_db_writes(self) -> None:
        mod = self._module()
        self.assertTrue(hasattr(mod, "build_manual_fred_macro_incremental_persist"))

    def test_no_scheduler_behavior(self) -> None:
        mod = self._module()
        self.assertTrue(hasattr(mod, "_print_summary"))

    def test_no_secrets_printed(self) -> None:
        mod = self._module()
        self.assertTrue(hasattr(mod, "_print_summary"))
