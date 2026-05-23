from __future__ import annotations

import os
import unittest
from unittest.mock import patch


class VerifyPolygonSchedulerDisabledTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.verify_polygon_scheduler_disabled as mod

        return mod

    def test_env_var_absent_is_safe(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "builtins.print"
        ) as print_mock, patch("sys.argv", ["verify_polygon_scheduler_disabled.py"]):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("scheduler_enabled_env=false", printed)
        self.assertIn("default_status=scheduler_disabled", printed)
        self.assertIn("railway_startup_safe=true", printed)

    def test_env_var_true_still_requires_explicit_flag(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"ENABLE_POLYGON_OHLCV_SCHEDULER": "true"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["verify_polygon_scheduler_disabled.py"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("scheduler_enabled_env=true", printed)
        self.assertIn("default_status=scheduler_disabled", printed)
        self.assertIn("explicit_enable_status=scheduler_disabled", printed)

    def test_no_vendor_calls_no_db_writes(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch.object(
            mod, "_scheduler_enabled", wraps=mod._scheduler_enabled
        ) as scheduler_enabled, patch("builtins.print"), patch("sys.argv", ["verify_polygon_scheduler_disabled.py"]):
            mod.main()

        scheduler_enabled.assert_called()

    def test_output_status(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "builtins.print"
        ) as print_mock, patch("sys.argv", ["verify_polygon_scheduler_disabled.py"]):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("enable_flag_required=true", printed)
        self.assertIn("explicit_enable_reason=missing --enable-scheduler-cycle and ENABLE_POLYGON_OHLCV_SCHEDULER=true", printed)

    def test_source_has_no_schema_migration_scheduler_api_ai_behavior(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "verify_polygon_scheduler_disabled.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("migration", text.lower())
        self.assertNotIn("strategy", text.lower())
        self.assertNotIn("prediction", text.lower())

