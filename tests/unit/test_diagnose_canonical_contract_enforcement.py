from __future__ import annotations

import unittest
from unittest.mock import patch


class DiagnoseCanonicalContractEnforcementTests(unittest.TestCase):
    def _module(self):
        import scripts.diagnose_canonical_contract_enforcement as mod

        return mod

    def _printed(self, mock_print) -> str:
        return "\n".join(" ".join(str(arg) for arg in call.args) for call in mock_print.mock_calls)

    def test_diagnostic_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch("sys.argv", ["diagnose_canonical_contract_enforcement.py"]):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("ingestion_repo_role=enforce_runtime_standards", printed)
        self.assertIn("data_repo_role=define_canonical_standards", printed)
        self.assertIn("contract_enforcement_status=planning_only_not_enabled", printed)
        self.assertIn("runtime_behavior_changed=false", printed)
        self.assertIn("production_switch_enabled=false", printed)

    def test_ownership_and_forbidden_overlap_present(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch("sys.argv", ["diagnose_canonical_contract_enforcement.py"]):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("ingestion_must_follow=schemas,timestamp_policy,lineage_standards,canonical_enums,field_names,quality_specifications,read_api_contracts", printed)
        self.assertIn("ingestion_may_own=vendor_fetching,retries,checkpoints,runtime_validation,normalization_execution,approved_writes,backfills,flat_files,websocket,scheduler_execution", printed)
        self.assertIn("ingestion_must_not_own=canonical_schema_definitions,migrations,canonical_table_structure,indexes,timestamp_policy_authority,lineage_contract_authority", printed)
        self.assertIn("enforcement_boundary=runtime_validators_must_trace_to_data_contracts", printed)
        self.assertIn("write_boundary=write_orchestration_allowed_schema_ownership_not_allowed", printed)

    def test_import_safety(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_canonical_contract_enforcement.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("DATABASE_URL", text)
        self.assertNotIn("POLYGON_API_KEY", text)
        self.assertNotIn("requests", text)
