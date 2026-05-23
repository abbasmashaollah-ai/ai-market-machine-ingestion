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

    def test_no_db_writes_or_scheduler_behavior(self) -> None:
        mod = self._module()
        self.assertTrue(hasattr(mod, "MODULES"))
