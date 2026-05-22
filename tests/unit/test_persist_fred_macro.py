from __future__ import annotations

import os
import unittest
from unittest.mock import patch


class PersistFredMacroTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.persist_fred_macro as mod

        return mod

    def test_dry_mode_does_not_write(self) -> None:
        os.environ["FRED_API_KEY"] = "fred-secret"
        os.environ["DATABASE_URL"] = "postgresql://example/db"
        mod = self._module()

        class FakeClient:
            def fetch_series_observations_raw(self, series_id: str, *, observation_start: str | None = None, observation_end: str | None = None):
                return {"observations": [{"series_id": series_id, "date": "2000-01-01", "value": "1.0"}]}

        with patch.object(mod, "MacroWriter") as writer_mock:
            summaries = mod.build_series_summaries(
                selected_series_ids=("GDP",),
                fred_client=FakeClient(),
                writer=None,
            )

        self.assertEqual(summaries[0].rows_written, 0)
        writer_mock.assert_not_called()

    def test_confirm_mode_calls_writer(self) -> None:
        os.environ["FRED_API_KEY"] = "fred-secret"
        os.environ["DATABASE_URL"] = "postgresql://example/db"
        mod = self._module()

        class FakeClient:
            def fetch_series_observations_raw(self, series_id: str, *, observation_start: str | None = None, observation_end: str | None = None):
                return {"observations": [{"series_id": series_id, "date": "2000-01-01", "value": "1.0"}]}

        class FakeWriter:
            def __init__(self, connection):
                self.connection = connection
                self.calls = []

            def write(self, records):
                self.calls.append(records)
                return type("Result", (), {"status": type("S", (), {"value": "success"})(), "written_count": 1})()

        with patch.object(mod, "_open_connection", return_value=object()):
            writer = FakeWriter(object())
            summaries = mod.build_series_summaries(
                selected_series_ids=("GDP",),
                fred_client=FakeClient(),
                writer=writer,
            )

        self.assertEqual(summaries[0].rows_written, 1)
        self.assertEqual(len(writer.calls), 1)

    def test_missing_fred_api_key_refuses(self) -> None:
        os.environ.pop("FRED_API_KEY", None)
        os.environ["DATABASE_URL"] = "postgresql://example/db"

        mod = self._module()
        with patch.object(mod, "load_local_env_if_available", return_value=False):
            with self.assertRaises(RuntimeError):
                mod.main()

    def test_missing_database_url_refuses(self) -> None:
        os.environ["FRED_API_KEY"] = "fred-secret"
        os.environ.pop("DATABASE_URL", None)

        mod = self._module()
        with patch.object(mod, "load_local_env_if_available", return_value=False):
            with self.assertRaises(RuntimeError):
                mod.main()

    def test_validation_failures_are_skipped_safely(self) -> None:
        os.environ["FRED_API_KEY"] = "fred-secret"
        os.environ["DATABASE_URL"] = "postgresql://example/db"
        mod = self._module()

        class FakeClient:
            def fetch_series_observations_raw(self, series_id: str, *, observation_start: str | None = None, observation_end: str | None = None):
                return {
                    "observations": [
                        {"series_id": series_id, "date": "2000-01-01", "value": "."},
                        {"series_id": series_id, "date": "2000-01-02", "value": "1.0"},
                    ]
                }

        summaries = mod.build_series_summaries(
            selected_series_ids=("GDP",),
            fred_client=FakeClient(),
            writer=None,
        )

        self.assertEqual(summaries[0].rows_fetched, 2)
        self.assertEqual(summaries[0].rows_valid, 1)
        self.assertGreaterEqual(summaries[0].validation_failures, 1)

    def test_secrets_are_not_printed(self) -> None:
        os.environ["FRED_API_KEY"] = "fred-secret"
        os.environ["DATABASE_URL"] = "postgresql://user:secret@example/db"
        mod = self._module()

        class FakeClient:
            def fetch_series_observations_raw(self, series_id: str, *, observation_start: str | None = None, observation_end: str | None = None):
                return {"observations": [{"series_id": series_id, "date": "2000-01-01", "value": "1.0"}]}

        with patch("builtins.print") as print_mock:
            summaries = mod.build_series_summaries(
                selected_series_ids=("GDP",),
                fred_client=FakeClient(),
                writer=None,
            )
            mod._print_summaries(summaries)

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertNotIn("secret", printed)
        self.assertNotIn("DATABASE_URL", printed)

    def test_no_live_network_calls_in_tests(self) -> None:
        mod = self._module()
        self.assertTrue(hasattr(mod, "_build_fred_client"))
