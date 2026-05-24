from __future__ import annotations

import unittest
from unittest.mock import patch


class DiagnoseIngestionEvidenceOutputContractTests(unittest.TestCase):
    def _module(self):
        import scripts.diagnose_ingestion_evidence_output_contract as mod

        return mod

    def _printed(self, mock_print) -> str:
        return "\n".join(" ".join(str(arg) for arg in call.args) for call in mock_print.mock_calls)

    def test_diagnostic_output_exists(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("ingestion_evidence_contract_status=planning_only_not_enabled", printed)
        self.assertIn("runtime_behavior_changed=false", printed)
        self.assertIn("production_switch_enabled=false", printed)

    def test_safety_flags_are_false(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main()
        printed = self._printed(print_mock)
        for field in [
            "db_reads_enabled=false",
            "db_writes_enabled=false",
            "vendor_calls_enabled=false",
            "scheduler_execution_enabled=false",
            "ingestion_execution_enabled=false",
            "canonical_schema_defined_in_ingestion=false",
        ]:
            self.assertIn(field, printed)

    def test_evidence_families_and_consumers_present(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn(
            "evidence_output_families=ingestion_run_history,data_quality_results,data_lineage_records,evidence_chain_verification,coverage_or_freshness_evidence,checkpoint_state,vendor_request_or_quota_evidence,error_and_retry_evidence",
            printed,
        )
        self.assertIn(
            "downstream_consumers=data_stored_evidence_health,grafana_read_models,operator_runbooks,production_scheduler_readiness",
            printed,
        )
        self.assertIn("data_repo_contract_source=ai-market-machine-data", printed)

    def test_no_db_vendor_scheduler_ingestion_calls(self) -> None:
        mod = self._module()
        source = mod.__file__
        self.assertIsNotNone(source)
        text = open(source, encoding="utf-8").read()
        self.assertNotIn("SessionLocal", text)
        self.assertNotIn("requests", text)
        self.assertNotIn("scheduler.start", text)
        self.assertNotIn("ingestion.execute", text)

    def test_import_safety(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_ingestion_evidence_output_contract.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("DATABASE_URL", text)
        self.assertNotIn("POLYGON_API_KEY", text)
        self.assertNotIn("requests", text)
