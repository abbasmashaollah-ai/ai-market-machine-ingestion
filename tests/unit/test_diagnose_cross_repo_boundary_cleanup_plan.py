from __future__ import annotations

import unittest
from unittest.mock import patch


class DiagnoseCrossRepoBoundaryCleanupPlanTests(unittest.TestCase):
    def _module(self):
        import scripts.diagnose_cross_repo_boundary_cleanup_plan as mod

        return mod

    def _printed(self, mock_print) -> str:
        return "\n".join(" ".join(str(arg) for arg in call.args) for call in mock_print.mock_calls)

    def test_output_contains_classifications(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch("sys.argv", ["diagnose_cross_repo_boundary_cleanup_plan.py"]):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("cleanup_plan_status=planning_only_not_enabled", printed)
        self.assertIn("destructive_actions_enabled=false", printed)
        self.assertIn("keep_in_data=schema,migrations,canonical_read_apis,grafana_read_models,stored_evidence_health", printed)
        self.assertIn("move_to_ingestion=vendor_fetching,daily_runners,backfills,flat_files,websocket,scheduler_execution", printed)
        self.assertIn("deprecate_in_data=direct_vendor_ingestion,old_runtime_ingestion_paths,direct_scheduler_execution", printed)
        self.assertIn("hygiene_cleanup=.env,.venv,.pytest_cache,__pycache__,logs_in_handoff_zips", printed)

    def test_required_next_steps_present(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch("sys.argv", ["diagnose_cross_repo_boundary_cleanup_plan.py"]):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("required_next_steps=confirm_data_repo_audit,mark_deprecated_paths,remove_runtime_invocation_paths_after_migration,clean_handoff_packaging", printed)

    def test_import_safety(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_cross_repo_boundary_cleanup_plan.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("DATABASE_URL", text)
        self.assertNotIn("POLYGON_API_KEY", text)
        self.assertNotIn("requests", text)
