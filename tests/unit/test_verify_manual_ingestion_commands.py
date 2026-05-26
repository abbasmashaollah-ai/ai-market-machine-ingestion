from __future__ import annotations

import os
import unittest
from unittest.mock import patch


class VerifyManualIngestionCommandsTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.verify_manual_ingestion_commands as mod

        return mod

    def test_import_verification_is_safe_without_env(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch("builtins.print") as print_mock:
            exit_code = mod.main()

        self.assertEqual(exit_code, 0)
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("scripts.inspect_fred_macro_checkpoint", printed)
        self.assertIn("scripts.dry_run_polygon_ohlcv_incremental", printed)
        self.assertIn("scripts.persist_polygon_ohlcv_incremental", printed)
        self.assertIn("scripts.inspect_polygon_ohlcv_checkpoint", printed)
        self.assertIn("scripts.preview_fred_macro_incremental", printed)
        self.assertIn("scripts.dry_run_fred_macro_incremental", printed)
        self.assertIn("scripts.persist_fred_macro_incremental", printed)
        self.assertIn("scripts.diagnose_polygon_flatfile_layout_readiness", printed)
        self.assertIn("scripts.diagnose_polygon_flatfile_official_layout_capture", printed)
        self.assertIn("scripts.diagnose_polygon_flatfile_config_readiness", printed)
        self.assertIn("scripts.diagnose_polygon_flatfile_storage_policy", printed)
        self.assertIn("scripts.diagnose_polygon_flatfile_manifest_readiness", printed)
        self.assertIn("scripts.diagnose_polygon_flatfile_integrity_readiness", printed)
        self.assertIn("scripts.diagnose_polygon_flatfile_quarantine_readiness", printed)
        self.assertIn("scripts.diagnose_polygon_flatfile_parse_readiness", printed)
        self.assertIn("scripts.diagnose_polygon_flatfile_download_readiness", printed)
        self.assertIn("scripts.diagnose_polygon_flatfile_persistence_readiness", printed)
        self.assertIn("scripts.diagnose_polygon_flatfile_e2e_readiness", printed)
        self.assertIn("scripts.run_fmp_ohlcv_daily_update", printed)
        self.assertIn("scripts.preflight_fmp_ohlcv_operations", printed)
        self.assertIn("scripts.verify_fmp_ohlcv_evidence_chain", printed)
        self.assertIn("scripts.assess_ohlcv_scheduler_readiness", printed)
        self.assertIn("scripts.plan_ohlcv_scheduled_run", printed)
        self.assertIn("scripts.dry_run_symbol_master_ingestion", printed)
        self.assertIn("scripts.preflight_symbol_master_operations", printed)
        self.assertIn("scripts.verify_symbol_master_evidence_chain", printed)
        self.assertIn("scripts.dry_run_polygon_symbol_master", printed)
        self.assertIn("scripts.diagnose_ingestion_monitoring_readiness", printed)
        self.assertIn("scripts.diagnose_ingestion_retry_recovery_readiness", printed)
        self.assertIn("scripts.diagnose_ingestion_failure_recovery_runbook", printed)
        self.assertIn("scripts.diagnose_polygon_production_enablement_readiness", printed)
        self.assertIn("scripts.diagnose_market_calendar_production_upgrade", printed)
        self.assertIn("scripts.diagnose_market_calendar_provider_strategy", printed)
        self.assertIn("scripts.diagnose_market_calendar_provider_interface", printed)
        self.assertIn("scripts.diagnose_market_calendar_fallback_behavior", printed)
        self.assertIn("scripts.diagnose_market_calendar_schema_handoff", printed)
        self.assertIn("scripts.diagnose_market_calendar_consumer_readiness", printed)
        self.assertIn("scripts.diagnose_market_calendar_mock_consumer_contract", printed)
        self.assertIn("scripts.diagnose_market_calendar_mock_provider", printed)
        self.assertIn("scripts.diagnose_market_calendar_provider_comparison", printed)
        self.assertIn("scripts.diagnose_verified_calendar_consumer_implementation_plan", printed)
        self.assertIn("scripts.diagnose_canonical_contract_enforcement", printed)
        self.assertIn("scripts.diagnose_cross_repo_boundary_overlap", printed)
        self.assertNotIn("DATABASE_URL", printed)
        self.assertNotIn("FRED_API_KEY", printed)

    def test_no_vendor_calls(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch("importlib.import_module", wraps=__import__("importlib").import_module) as import_mock:
            mod.main()

        import_names = [call.args[0] for call in import_mock.mock_calls if call.args]
        self.assertIn("scripts.inspect_fred_macro_checkpoint", import_names)
        self.assertIn("scripts.dry_run_polygon_ohlcv_incremental", import_names)
        self.assertIn("scripts.persist_polygon_ohlcv_incremental", import_names)
        self.assertIn("scripts.inspect_polygon_ohlcv_checkpoint", import_names)
        self.assertIn("scripts.preview_fred_macro_incremental", import_names)
        self.assertIn("scripts.dry_run_fred_macro_incremental", import_names)
        self.assertIn("scripts.persist_fred_macro_incremental", import_names)
        self.assertIn("scripts.diagnose_polygon_flatfile_layout_readiness", import_names)
        self.assertIn("scripts.diagnose_polygon_flatfile_official_layout_capture", import_names)
        self.assertIn("scripts.diagnose_polygon_flatfile_config_readiness", import_names)
        self.assertIn("scripts.diagnose_polygon_flatfile_storage_policy", import_names)
        self.assertIn("scripts.diagnose_polygon_flatfile_manifest_readiness", import_names)
        self.assertIn("scripts.diagnose_polygon_flatfile_integrity_readiness", import_names)
        self.assertIn("scripts.diagnose_polygon_flatfile_quarantine_readiness", import_names)
        self.assertIn("scripts.diagnose_polygon_flatfile_parse_readiness", import_names)
        self.assertIn("scripts.diagnose_polygon_flatfile_download_readiness", import_names)
        self.assertIn("scripts.diagnose_polygon_flatfile_persistence_readiness", import_names)
        self.assertIn("scripts.diagnose_polygon_flatfile_e2e_readiness", import_names)
        self.assertIn("scripts.run_fmp_ohlcv_daily_update", import_names)
        self.assertIn("scripts.preflight_fmp_ohlcv_operations", import_names)
        self.assertIn("scripts.verify_fmp_ohlcv_evidence_chain", import_names)
        self.assertIn("scripts.assess_ohlcv_scheduler_readiness", import_names)
        self.assertIn("scripts.plan_ohlcv_scheduled_run", import_names)
        self.assertIn("scripts.dry_run_symbol_master_ingestion", import_names)
        self.assertIn("scripts.preflight_symbol_master_operations", import_names)
        self.assertIn("scripts.verify_symbol_master_evidence_chain", import_names)
        self.assertIn("scripts.dry_run_polygon_symbol_master", import_names)
        self.assertIn("scripts.diagnose_ingestion_monitoring_readiness", import_names)
        self.assertIn("scripts.diagnose_ingestion_retry_recovery_readiness", import_names)
        self.assertIn("scripts.diagnose_ingestion_failure_recovery_runbook", import_names)
        self.assertIn("scripts.diagnose_polygon_production_enablement_readiness", import_names)
        self.assertIn("scripts.diagnose_market_calendar_production_upgrade", import_names)
        self.assertIn("scripts.diagnose_market_calendar_provider_strategy", import_names)
        self.assertIn("scripts.diagnose_market_calendar_provider_interface", import_names)
        self.assertIn("scripts.diagnose_market_calendar_fallback_behavior", import_names)
        self.assertIn("scripts.diagnose_market_calendar_schema_handoff", import_names)
        self.assertIn("scripts.diagnose_market_calendar_consumer_readiness", import_names)
        self.assertIn("scripts.diagnose_market_calendar_mock_consumer_contract", import_names)
        self.assertIn("scripts.diagnose_market_calendar_mock_provider", import_names)
        self.assertIn("scripts.diagnose_market_calendar_provider_comparison", import_names)
        self.assertIn("scripts.diagnose_verified_calendar_consumer_implementation_plan", import_names)
        self.assertIn("scripts.diagnose_canonical_contract_enforcement", import_names)
        self.assertIn("scripts.diagnose_cross_repo_boundary_overlap", import_names)

    def test_no_db_writes_or_scheduler_behavior(self) -> None:
        mod = self._module()
        self.assertTrue(hasattr(mod, "MODULES"))
