from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch


class PlanPolygonSymbolMasterPopulationTests(unittest.TestCase):
    def _module(self):
        import scripts.plan_polygon_symbol_master_population as mod

        return mod

    def test_plan_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            exit_code = mod.main()

        self.assertEqual(exit_code, 0)
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("no_vendor_calls=True", printed)
        self.assertIn("no_db_writes=True", printed)
        self.assertIn("safe_default_batch_size=25", printed)
        self.assertIn("max_records_recommendation=1000", printed)
        self.assertIn("required_env_live_check=POLYGON_API_KEY", printed)
        self.assertIn("required_env_confirm_write=DATABASE_URL", printed)
        self.assertIn("coverage_thresholds=min_total=1 min_active=1", printed)
        self.assertIn("scripts/preflight_symbol_master_operations.py", printed)
        self.assertIn("scripts/dry_run_polygon_symbol_master.py", printed)
        self.assertIn("scripts/assess_symbol_master_coverage.py", printed)
        self.assertIn("scripts/verify_symbol_master_evidence_chain.py", printed)

    def test_no_vendor_calls_or_db_writes(self) -> None:
        mod = self._module()
        with patch("builtins.print"), patch("importlib.import_module") as import_mock:
            mod.main()

        import_mock.assert_not_called()

    def test_no_forbidden_imports(self) -> None:
        text = Path("scripts/plan_polygon_symbol_master_population.py").read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("alembic", text.lower())
        self.assertNotIn("ai_market_machine_data", text)
        self.assertNotIn("requests", text.lower())
        self.assertNotIn("httpx", text.lower())

    def test_docs_cover_runbook(self) -> None:
        text = Path("docs/symbol_master_polygon_population_runbook.md").read_text(encoding="utf-8").lower()
        self.assertIn("symbol master polygon population runbook", text)
        self.assertIn("preflight", text)
        self.assertIn("coverage assessment", text)
        self.assertIn("what not to do", text)
