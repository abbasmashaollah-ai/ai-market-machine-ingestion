from __future__ import annotations

import os
import unittest
from unittest.mock import patch


class DiagnosePolygonFlatfileStoragePolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.diagnose_polygon_flatfile_storage_policy as mod

        return mod

    def _printed(self, mock_print) -> str:
        return "\n".join(" ".join(str(arg) for arg in call.args) for call in mock_print.mock_calls)

    def test_no_storage_root(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["diagnose_polygon_flatfile_storage_policy.py"],
        ):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("storage_root_configured=false", printed)
        self.assertIn("storage_root_source=none", printed)
        self.assertIn("storage_policy_status=planning_only_not_enabled", printed)
        self.assertIn("writes_enabled=false", printed)

    def test_cli_storage_root(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["diagnose_polygon_flatfile_storage_policy.py", "--storage-root", "C:/data/polygon-flatfiles"],
        ):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("storage_root_configured=true", printed)
        self.assertIn("storage_root_source=cli", printed)
        self.assertIn("storage_policy_status=planning_only_not_enabled", printed)

    def test_env_storage_root(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"POLYGON_FLATFILE_STORAGE_ROOT": "C:/data/polygon-flatfiles"}, clear=True), patch(
            "builtins.print"
        ) as print_mock, patch("sys.argv", ["diagnose_polygon_flatfile_storage_policy.py"]):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("storage_root_configured=true", printed)
        self.assertIn("storage_root_source=env", printed)

    def test_repo_root_unsafe_path_detection(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["diagnose_polygon_flatfile_storage_policy.py", "--storage-root", "C:/repo/app/data"],
        ):
            mod.main()
        printed = self._printed(print_mock)
        self.assertIn("storage_policy_status=manual_review_needed", printed)

    def test_import_safety(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "diagnose_polygon_flatfile_storage_policy.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("POLYGON_API_KEY", text)
        self.assertNotIn("DATABASE_URL", text)
        self.assertNotIn("S3", text)
        self.assertNotIn("mkdir", text)
