from __future__ import annotations

import unittest
from unittest.mock import patch


class DiagnoseCrossRepoBoundaryOverlapTests(unittest.TestCase):
    def _module(self):
        import scripts.diagnose_cross_repo_boundary_overlap as mod

        return mod

    def _printed(self, mock_print) -> str:
        return "\n".join(" ".join(str(arg) for arg in call.args) for call in mock_print.mock_calls)

    def test_output_contains_categories(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch("sys.argv", ["diagnose_cross_repo_boundary_overlap.py"]):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("audit_status=read_only", printed)
        self.assertIn("cross_repo_boundary=ai-market-machine-data_vs_ai-market-machine-ingestion", printed)
        self.assertIn("data_owned_schema=", printed)
        self.assertIn("data_owned_read_api=", printed)
        self.assertIn("data_owned_grafana_monitoring=", printed)
        self.assertIn("ingestion_overlap_runtime=", printed)
        self.assertIn("ingestion_overlap_scheduler=", printed)
        self.assertIn("ingestion_overlap_vendor_clients=", printed)
        self.assertIn("ingestion_overlap_mutation_endpoints=", printed)
        self.assertIn("legacy_or_deprecate=", printed)
        self.assertIn("boundary_audit_status=diagnostic_only", printed)
        self.assertIn("production_switch_enabled=false", printed)

    def test_packaging_hygiene_flags_present(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch("sys.argv", ["diagnose_cross_repo_boundary_overlap.py"]):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn(".git=", printed)
        self.assertIn("__pycache__=", printed)
        self.assertIn(".pytest_cache=", printed)
        self.assertIn("logs=", printed)

    def test_import_safety(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_cross_repo_boundary_overlap.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("DATABASE_URL", text)
        self.assertNotIn("POLYGON_API_KEY", text)
        self.assertNotIn("requests", text)
