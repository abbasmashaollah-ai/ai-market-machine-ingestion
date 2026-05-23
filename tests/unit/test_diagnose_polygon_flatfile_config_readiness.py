from __future__ import annotations

import os
import unittest
from unittest.mock import patch


class DiagnosePolygonFlatfileConfigReadinessTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.diagnose_polygon_flatfile_config_readiness as mod

        return mod

    def _printed(self, mock_print) -> str:
        return "\n".join(" ".join(str(arg) for arg in call.args) for call in mock_print.mock_calls)

    def test_no_env_vars(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch("builtins.print") as print_mock:
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("access_key_configured=false", printed)
        self.assertIn("secret_key_configured=false", printed)
        self.assertIn("bucket_configured=false", printed)
        self.assertIn("endpoint_configured=false", printed)
        self.assertIn("region_configured=false", printed)
        self.assertIn("storage_root_configured=false", printed)
        self.assertIn("config_readiness_status=not_configured", printed)
        self.assertIn("flatfile_download_enabled=false", printed)
        self.assertIn("flatfile_discovery_enabled=false", printed)

    def test_partial_env_vars(self) -> None:
        mod = self._module()
        env = {
            "POLYGON_FLATFILE_ACCESS_KEY_ID": "present",
            "POLYGON_FLATFILE_BUCKET": "present",
        }
        with patch.dict(os.environ, env, clear=True), patch("builtins.print") as print_mock:
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("access_key_configured=true", printed)
        self.assertIn("bucket_configured=true", printed)
        self.assertIn("secret_key_configured=false", printed)
        self.assertIn("config_readiness_status=partial_configured", printed)
        self.assertNotIn("present", printed)

    def test_all_env_vars_present(self) -> None:
        mod = self._module()
        env = {name: "present" for name in mod.ENV_VARS}
        with patch.dict(os.environ, env, clear=True), patch("builtins.print") as print_mock:
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("access_key_configured=true", printed)
        self.assertIn("secret_key_configured=true", printed)
        self.assertIn("bucket_configured=true", printed)
        self.assertIn("endpoint_configured=true", printed)
        self.assertIn("region_configured=true", printed)
        self.assertIn("storage_root_configured=true", printed)
        self.assertIn("config_readiness_status=configured_but_disabled", printed)
        self.assertNotIn("present", printed)

    def test_import_safety(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_polygon_flatfile_config_readiness.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("POLYGON_API_KEY", text)
        self.assertNotIn("DATABASE_URL", text)
        self.assertNotIn("S3", text)
        self.assertNotIn("requests", text)
