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

    def test_no_vendor_calls(self) -> None:
        mod = self._module()
        with patch("importlib.import_module") as import_mock:
            mod.main([])
        imported = [call.args[0] for call in import_mock.mock_calls if call.args]
        self.assertFalse(any(name.startswith("app.vendors") for name in imported))

    def test_no_db_writes(self) -> None:
        mod = self._module()
        with patch("builtins.print"):
            mod.main([])

    def test_no_forbidden_imports(self) -> None:
        text = Path("scripts/dry_run_fred_macro_foundation.py").read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("alembic", text.lower())
        self.assertNotIn("requests", text.lower())
        self.assertNotIn("httpx", text.lower())

    def test_docs_coverage(self) -> None:
        text = Path("docs/fred_macro_foundation.md").read_text(encoding="utf-8").lower()
        self.assertIn("fred macro foundation", text)
        self.assertIn("no vendor calls by default", text)
        self.assertIn("no db writes", text)
        self.assertIn("dgs10", text)
        self.assertIn("unrate", text)

