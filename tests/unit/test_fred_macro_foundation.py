from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest.mock import patch


class FredMacroFoundationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.dry_run_fred_macro_foundation as mod

        return mod

    def _preflight_module(self):
        import scripts.preflight_fred_macro_operations as mod

        return mod

    def test_normalization_behavior(self) -> None:
        from app.normalization.fred_macro import FredMacroSeriesDefinition, normalize_fred_macro_record

        record = normalize_fred_macro_record(
            {"series_id": "DGS10", "date": "2026-01-01", "value": "4.12"},
            FredMacroSeriesDefinition("DGS10", "percent", "daily", "10-year Treasury constant maturity rate"),
        )
        self.assertIsNotNone(record)
        assert record is not None
        self.assertEqual(record.series_id, "DGS10")
        self.assertEqual(str(record.observation_date), "2026-01-01")
        self.assertEqual(record.value, 4.12)
        self.assertEqual(record.source, "fred")

    def test_starter_series_deterministic(self) -> None:
        from app.normalization.fred_macro import get_starter_fred_macro_series

        series = get_starter_fred_macro_series()
        self.assertEqual([item.series_id for item in series], ["DGS10", "DGS2", "FEDFUNDS", "CPIAUCSL", "UNRATE"])

    def test_dry_run_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main([])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("series_count=5", printed)
        self.assertIn("requested_series=", printed)
        self.assertIn("normalized_count=5", printed)
        self.assertIn("valid_count=5", printed)
        self.assertIn("invalid_count=0", printed)
        self.assertIn("no_vendor_calls=True", printed)
        self.assertIn("no_db_writes=True", printed)

    def test_show_series_behavior(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main(["--show-series"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("series=[", printed)
        self.assertIn("DGS10", printed)

    def test_show_values_behavior(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main(["--show-values"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("normalized_values=[", printed)

    def test_no_vendor_calls(self) -> None:
        mod = self._module()
        with patch("builtins.print"), patch("scripts.dry_run_fred_macro_foundation.UnsupportedFredClient") as client_mock:
            mod.main([])
        client_mock.assert_not_called()

    def test_no_db_writes(self) -> None:
        mod = self._module()
        with patch("builtins.print"):
            mod.main([])

    def test_live_check_normalization(self) -> None:
        mod = self._module()
        fake_result = type(
            "FakeResult",
            (),
            {
                "records": (
                    type("Record", (), {"value": 1.0})(),
                    type("Record", (), {"value": 2.0})(),
                ),
                "invalid_rows": (),
                "latest_observation_date": "2026-01-02",
            },
        )()
        with patch.dict(os.environ, {"FRED_API_KEY": "secret"}, clear=True), patch.object(
            mod, "_load_local_env_if_available", return_value=False
        ), patch.object(mod, "fetch_fred_macro_series", return_value=fake_result) as fetch_mock, patch(
            "builtins.print"
        ) as print_mock:
            mod.main(["--live-check", "--series", "DGS10"])
        fetch_mock.assert_called_once()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("requested_series=['DGS10']", printed)
        self.assertIn("latest_observation_dates={'DGS10': '2026-01-02'}", printed)

    def test_live_check_newest_observations_and_latest_date(self) -> None:
        from app.normalization.fred_macro import FredMacroSeriesDefinition
        from app.vendors.fred_macro import fetch_fred_macro_series

        class FakeClient:
            def fetch_series_observations_raw(self, series_id: str, *, observation_start: str | None = None, observation_end: str | None = None):
                return {
                    "observations": [
                        {"series_id": series_id, "date": "2026-01-01", "value": "1.0"},
                        {"series_id": series_id, "date": "2026-01-03", "value": "3.0"},
                        {"series_id": series_id, "date": "2026-01-02", "value": "2.0"},
                    ]
                }

        result = fetch_fred_macro_series(
            FakeClient(),
            FredMacroSeriesDefinition("DGS10", "percent", "daily", "10-year Treasury constant maturity rate"),
            max_observations=2,
        )
        self.assertEqual([record.observation_date.isoformat() for record in result.records], ["2026-01-02", "2026-01-03"])
        self.assertEqual(result.latest_observation_date, "2026-01-03")
        self.assertEqual(result.requested_count, 2)

    def test_missing_invalid_series_handling(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"FRED_API_KEY": "secret"}, clear=True), patch.object(
            mod, "_load_local_env_if_available", return_value=False
        ), patch.object(mod, "fetch_fred_macro_series") as fetch_mock, patch("builtins.print") as print_mock:
            mod.main(["--live-check", "--series", "UNKNOWN", "--show-invalid"])
        fetch_mock.assert_not_called()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("invalid_count=1", printed)
        self.assertIn("missing_or_unsupported_series", printed)

    def test_fixture_behavior_remains_deterministic(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main([])
        first = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        with patch("builtins.print") as print_mock_again:
            mod.main([])
        second = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock_again.mock_calls)
        self.assertEqual(first, second)

    def test_no_forbidden_imports(self) -> None:
        text = Path("scripts/dry_run_fred_macro_foundation.py").read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("alembic", text.lower())
        self.assertNotIn("requests", text.lower())
        self.assertNotIn("httpx", text.lower())
        vendor_text = Path("app/vendors/fred_macro.py").read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", vendor_text)
        self.assertNotIn("APIRouter", vendor_text)
        self.assertNotIn("alembic", vendor_text.lower())
        self.assertNotIn("requests", vendor_text.lower())
        self.assertNotIn("httpx", vendor_text.lower())

    def test_docs_coverage(self) -> None:
        text = Path("docs/fred_macro_foundation.md").read_text(encoding="utf-8").lower()
        self.assertIn("fred macro foundation", text)
        self.assertIn("no vendor calls by default", text)
        self.assertIn("no db writes", text)
        self.assertIn("dgs10", text)
        self.assertIn("unrate", text)

    def test_live_dry_run_doc(self) -> None:
        text = Path("docs/fred_macro_live_dry_run.md").read_text(encoding="utf-8").lower()
        self.assertIn("live dry-run", text)
        self.assertIn("no db writes", text)
        self.assertIn("api key is only required for `--live-check`", text)

    def test_preflight_pass(self) -> None:
        mod = self._preflight_module()
        with patch("builtins.print") as print_mock:
            exit_code = mod.main([])
        self.assertEqual(exit_code, 0)
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("dry_run_command_exists=True", printed)
        self.assertIn("live_dry_run_doc_exists=True", printed)
        self.assertIn("normalization_module_exists=True", printed)
        self.assertIn("starter_series_configured=True", printed)
        self.assertIn("forbidden_imports_absent=True", printed)

    def test_preflight_live_check_requires_api_key(self) -> None:
        mod = self._preflight_module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "_load_local_env_if_available", return_value=False):
            with self.assertRaises(RuntimeError):
                mod.main(["--live-check"])

    def test_preflight_no_database_url_requirement(self) -> None:
        mod = self._preflight_module()
        with patch.dict(os.environ, {}, clear=True), patch("builtins.print") as print_mock:
            mod.main([])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("no_database_url_required_yet=True", printed)

    def test_preflight_docs_coverage(self) -> None:
        preflight_doc = Path("docs/fred_macro_preflight.md").read_text(encoding="utf-8").lower()
        evidence_doc = Path("docs/fred_macro_evidence_plan.md").read_text(encoding="utf-8").lower()
        self.assertIn("dry-run foundation", preflight_doc)
        self.assertIn("database_url is not required yet", preflight_doc)
        self.assertIn("macro row counts by series", evidence_doc)
        self.assertIn("latest observation date by series", evidence_doc)
        self.assertIn("no db reads yet", evidence_doc)
        self.assertIn("no db writes yet", evidence_doc)
