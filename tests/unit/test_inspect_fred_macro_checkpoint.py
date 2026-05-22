from __future__ import annotations

import os
import unittest
from datetime import date, datetime, timezone
from unittest.mock import Mock, patch


class InspectFredMacroCheckpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.inspect_fred_macro_checkpoint as mod

        return mod

    def test_inspect_cli_prints_checkpoint_safely(self) -> None:
        mod = self._module()
        checkpoint = type(
            "Checkpoint",
            (),
            {
                "checkpoint_key": "fred:macro_observations:GDP:1d:2025-01-01:2025-12-31",
                "series_id": "GDP",
                "status": type("Status", (), {"value": "completed"})(),
                "planned_start_date": date(2025, 1, 1),
                "planned_end_date": date(2025, 12, 31),
                "last_successful_observation_date": date(2025, 10, 1),
                "updated_at": datetime(2025, 10, 2, 12, 0, tzinfo=timezone.utc),
            },
        )()

        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection") as open_connection, patch.object(
            mod, "ManualFREDMacroCheckpointStore"
        ) as store_cls, patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "inspect_fred_macro_checkpoint.py",
                "--series-id",
                "GDP",
                "--start-date",
                "2025-01-01",
                "--end-date",
                "2025-12-31",
            ],
        ):
            store = Mock()
            store.load.return_value = checkpoint
            store_cls.return_value = store
            open_connection.return_value = Mock()

            exit_code = mod.main()

        self.assertEqual(exit_code, 0)
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("checkpoint_found=true", printed)
        self.assertIn("checkpoint_key=fred:macro_observations:GDP:1d:2025-01-01:2025-12-31", printed)
        self.assertIn("last_successful_observation_date=2025-10-01", printed)
        self.assertNotIn("DATABASE_URL", printed)
        self.assertNotIn("secret", printed)
        store.load.assert_called_once()
        open_connection.assert_called_once()

    def test_inspect_cli_requires_database_url_but_not_fred_key(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch(
            "sys.argv",
            [
                "inspect_fred_macro_checkpoint.py",
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

    def test_inspect_cli_does_not_call_fred(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection") as open_connection, patch.object(
            mod, "ManualFREDMacroCheckpointStore"
        ) as store_cls, patch(
            "sys.argv",
            [
                "inspect_fred_macro_checkpoint.py",
                "--series-id",
                "GDP",
                "--start-date",
                "2025-01-01",
                "--end-date",
                "2025-12-31",
            ],
        ):
            store = Mock()
            store.load.return_value = None
            store_cls.return_value = store
            open_connection.return_value = Mock()

            mod.main()

        store.load.assert_called_once()
        open_connection.assert_called_once()

    def test_inspect_cli_supports_multiple_series(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection") as open_connection, patch.object(
            mod, "ManualFREDMacroCheckpointStore"
        ) as store_cls, patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "inspect_fred_macro_checkpoint.py",
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
            store = Mock()
            store.load.side_effect = [None, None]
            store_cls.return_value = store
            open_connection.return_value = Mock()

            exit_code = mod.main()

        self.assertEqual(exit_code, 0)
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("checkpoint_total=2 checkpoint_found_total=0", printed)
        self.assertEqual(store.load.call_count, 2)
