from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from scripts.smoke_macro_writer_db import SMOKE_SERIES_ID, main, run_smoke_check


class SmokeMacroWriterDbTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def test_refuses_to_write_without_confirm_flag(self) -> None:
        os.environ["DATABASE_URL"] = "sqlite:///ignored.db"

        result = run_smoke_check(confirm_write=False)

        self.assertFalse(result.would_write)
        self.assertIn("Dry check only", result.message)

    def test_script_does_not_print_database_url(self) -> None:
        os.environ["DATABASE_URL"] = "sqlite:///ignored.db"

        with patch("builtins.print") as print_mock:
            run_smoke_check(confirm_write=False)

        printed = " ".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertNotIn("DATABASE_URL", printed)

    def test_smoke_series_id_is_used(self) -> None:
        self.assertEqual(SMOKE_SERIES_ID, "INGESTION_SMOKE_TEST")

    def test_main_dry_check_reports_without_db_mutation(self) -> None:
        os.environ["DATABASE_URL"] = "sqlite:///ignored.db"

        with patch("scripts.smoke_macro_writer_db.run_smoke_check") as run_mock:
            run_mock.return_value.database_url_present = True
            run_mock.return_value.confirm_write = False
            run_mock.return_value.would_write = False
            run_mock.return_value.message = "Dry check only."
            with patch("builtins.print"):
                exit_code = main()

        self.assertEqual(exit_code, 0)
        run_mock.assert_called_once_with(confirm_write=False)

    def test_script_requires_database_url(self) -> None:
        os.environ.pop("DATABASE_URL", None)

        result = run_smoke_check(confirm_write=True)

        self.assertFalse(result.database_url_present)
        self.assertEqual(result.message, "DATABASE_URL is not set")
