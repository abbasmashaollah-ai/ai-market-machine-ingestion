from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch


class SymbolMasterSourcePlanTests(unittest.TestCase):
    def _module(self):
        import app.sources.symbol_master_sources as mod

        return mod

    def test_source_plan_shape(self) -> None:
        mod = self._module()
        plans = mod.build_symbol_master_source_plan()
        self.assertGreaterEqual(len(plans), 5)
        self.assertEqual(plans[0].source_name, "FMP")
        self.assertEqual(plans[1].source_name, "Polygon")
        self.assertEqual(plans[-1].source_name, "manual fixture")
        self.assertEqual(plans[-1].status, "test_only")

    def test_source_plan_includes_fmp_and_polygon(self) -> None:
        mod = self._module()
        names = [plan.source_name for plan in mod.build_symbol_master_source_plan()]
        self.assertIn("FMP", names)
        self.assertIn("Polygon", names)

    def test_manual_fixture_marked_test_only(self) -> None:
        mod = self._module()
        manual = [plan for plan in mod.build_symbol_master_source_plan() if plan.source_name == "manual fixture"][0]
        self.assertEqual(manual.status, "test_only")

    def test_command_output(self) -> None:
        import scripts.plan_symbol_master_sources as cmd

        with patch("builtins.print") as print_mock:
            cmd.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("no_vendor_calls=True", printed)
        self.assertIn("dry_run=True", printed)
        self.assertIn("selected_preferred_source=FMP", printed)
        self.assertIn("priority_order", printed)
        self.assertIn("next_required_step", printed)

    def test_no_vendor_calls_or_db_writes(self) -> None:
        import scripts.plan_symbol_master_sources as cmd

        with patch("builtins.print"), patch("importlib.import_module") as import_mock:
            cmd.main()

        import_mock.assert_not_called()

    def test_no_forbidden_imports(self) -> None:
        text = Path("scripts/plan_symbol_master_sources.py").read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("requests", text.lower())
        self.assertNotIn("httpx", text.lower())
        self.assertNotIn("alembic", text.lower())
        self.assertNotIn("ai_market_machine_data", text)

    def test_docs_cover_source_plan(self) -> None:
        text = Path("docs/symbol_master_source_plan.md").read_text(encoding="utf-8").lower()
        self.assertIn("symbol master source plan", text)
        self.assertIn("fmp", text)
        self.assertIn("polygon", text)
        self.assertIn("manual fixture", text)
