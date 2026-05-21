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
        os.environ["DATABASE_URL"] = "postgresql://example/db"

        with patch("scripts.smoke_macro_writer_db._open_connection") as open_mock:
            result = run_smoke_check(confirm_write=False)

        self.assertFalse(result.would_write)
        self.assertIn("Dry check only", result.message)
        open_mock.assert_not_called()

    def test_script_does_not_print_database_url(self) -> None:
        os.environ["DATABASE_URL"] = "postgresql://example/db"

        with patch("builtins.print") as print_mock:
            run_smoke_check(confirm_write=False)

        printed = " ".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertNotIn("DATABASE_URL", printed)

    def test_smoke_series_id_is_used(self) -> None:
        self.assertEqual(SMOKE_SERIES_ID, "INGESTION_SMOKE_TEST")

    def test_main_dry_check_reports_without_db_mutation(self) -> None:
        os.environ["DATABASE_URL"] = "postgresql://example/db"

        with patch("scripts.smoke_macro_writer_db.run_smoke_check") as run_mock:
            run_mock.return_value.database_url_present = True
            run_mock.return_value.confirm_write = False
            run_mock.return_value.would_write = False
            run_mock.return_value.status = "dry"
            run_mock.return_value.written_count = 0
            run_mock.return_value.skipped_count = 0
            run_mock.return_value.failed_count = 0
            run_mock.return_value.error_type = None
            run_mock.return_value.sanitized_error_message = None
            run_mock.return_value.message = "Dry check only."
            with patch("builtins.print"):
                exit_code = main()

        self.assertEqual(exit_code, 0)
        run_mock.assert_called_once_with(confirm_write=False)

    def test_script_requires_database_url(self) -> None:
        os.environ.pop("DATABASE_URL", None)

        with patch("scripts.smoke_macro_writer_db.load_local_env_if_available", return_value=False):
            result = run_smoke_check(confirm_write=True)

        self.assertFalse(result.database_url_present)
        self.assertEqual(result.message, "DATABASE_URL is not set")

    def test_postgres_url_allowed_only_with_confirm_write(self) -> None:
        os.environ["DATABASE_URL"] = "postgresql://example/db"

        with patch("scripts.smoke_macro_writer_db._open_connection") as open_mock:
            result = run_smoke_check(confirm_write=False)

        self.assertFalse(result.would_write)
        open_mock.assert_not_called()

    def test_postgres_confirmed_write_uses_connection(self) -> None:
        os.environ["DATABASE_URL"] = "postgresql://example/db"

        class FakeConnection:
            def close(self) -> None:
                return None

        fake_result = type(
            "Result",
            (),
            {"status": type("S", (), {"value": "success"})(), "written_count": 1, "skipped_count": 0, "failed_count": 0},
        )()

        with patch("scripts.smoke_macro_writer_db._open_connection") as open_mock:
            open_mock.return_value = FakeConnection()
            with patch("scripts.smoke_macro_writer_db.MacroWriter") as writer_mock:
                writer_mock.return_value.write.return_value = fake_result
                result = run_smoke_check(confirm_write=True)

        self.assertTrue(result.would_write)
        open_mock.assert_called_once()
        writer_mock.assert_called_once()

    def test_unsupported_url_rejected(self) -> None:
        os.environ["DATABASE_URL"] = "sqlite:///ignored.db"

        result = run_smoke_check(confirm_write=True)

        self.assertFalse(result.would_write)
        self.assertIn("postgresql:// or postgres://", result.message)

    def test_missing_driver_message_is_clear(self) -> None:
        os.environ["DATABASE_URL"] = "postgresql://example/db"

        with patch("scripts.smoke_macro_writer_db._load_postgres_connect", side_effect=RuntimeError("PostgreSQL smoke writes require psycopg or psycopg2 to be installed.")):
            result = run_smoke_check(confirm_write=True)

        self.assertFalse(result.would_write)
        self.assertIn("psycopg or psycopg2", result.message)

    def test_failed_write_prints_sanitized_error_output(self) -> None:
        os.environ["DATABASE_URL"] = "postgresql://user:secret@example/db?password=secret"

        class FakeConnection:
            def close(self) -> None:
                return None

        with patch("scripts.smoke_macro_writer_db._open_connection", return_value=FakeConnection()):
            with patch("scripts.smoke_macro_writer_db.MacroWriter") as writer_mock:
                writer_mock.return_value.write.side_effect = RuntimeError(
                    "failed for DATABASE_URL=postgresql://user:secret@example/db?password=secret"
                )
                with patch("builtins.print") as print_mock:
                    result = run_smoke_check(confirm_write=True)
                    from scripts.smoke_macro_writer_db import main as smoke_main
                    with patch("scripts.smoke_macro_writer_db.run_smoke_check", return_value=result):
                        smoke_main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("status=failed", printed)
        self.assertIn("written=0 skipped=0 failed=0", printed)
        self.assertIn("error_type=RuntimeError", printed)
        self.assertIn("sanitized_error_message=", printed)
        self.assertNotIn("secret", printed)
        self.assertNotIn("DATABASE_URL", printed)
        self.assertNotIn("postgresql://user:secret@example/db", printed)

    def test_sqlalchemy_style_connection_string_is_redacted(self) -> None:
        os.environ["DATABASE_URL"] = "postgresql://example/db"

        class FakeConnection:
            def close(self) -> None:
                return None

        with patch("scripts.smoke_macro_writer_db._open_connection", return_value=FakeConnection()):
            with patch("scripts.smoke_macro_writer_db.MacroWriter") as writer_mock:
                writer_mock.return_value.write.side_effect = RuntimeError(
                    "sqlalchemy.exc.OperationalError: postgresql://user:secret@example/db password=secret"
                )
                result = run_smoke_check(confirm_write=True)

        self.assertEqual(result.status, "failed")
        self.assertEqual(result.error_type, "RuntimeError")
        self.assertNotIn("user:secret", result.sanitized_error_message or "")
        self.assertNotIn("password=secret", result.sanitized_error_message or "")
        self.assertNotIn("DATABASE_URL", result.sanitized_error_message or "")
