from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest.mock import patch


class PreflightFmpOhlcvOperationsTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.preflight_fmp_ohlcv_operations as mod

        return mod

    def test_success_without_db_or_vendor_key(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch(
            "scripts.manual_ohlcv_preflight.load_local_env_if_available", return_value=False
        ), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            ["preflight_fmp_ohlcv_operations.py", "--as-of-date", "2026-01-14"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("vendor=fmp", printed)
        self.assertIn("preflight_status=ready", printed)

    def test_check_existing_requires_database_url(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch(
            "scripts.manual_ohlcv_preflight.load_local_env_if_available", return_value=False
        ), patch(
            "sys.argv",
            ["preflight_fmp_ohlcv_operations.py", "--as-of-date", "2026-01-14", "--check-existing"],
        ):
            with self.assertRaises(RuntimeError):
                mod.main()

    def test_confirm_write_requires_vendor_key(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch(
            "scripts.manual_ohlcv_preflight.load_local_env_if_available", return_value=False
        ), patch(
            "sys.argv",
            ["preflight_fmp_ohlcv_operations.py", "--as-of-date", "2026-01-14", "--confirm-write"],
        ):
            with self.assertRaises(RuntimeError):
                mod.main()

    def test_over_budget_fails_before_db_access(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"FMP_API_KEY": "secret"}, clear=True), patch(
            "scripts.manual_ohlcv_preflight.load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection") as open_connection_mock, patch(
            "sys.argv",
            [
                "preflight_fmp_ohlcv_operations.py",
                "--as-of-date",
                "2026-01-14",
                "--symbol",
                "AAPL",
                "--symbol",
                "MSFT",
                "--symbol",
                "SPY",
                "--symbol",
                "QQQ",
                "--max-symbols",
                "10",
                "--max-requests",
                "1",
            ],
        ):
            mod.main()

        open_connection_mock.assert_not_called()

    def test_source_has_no_api_scheduler_or_migration_imports(self) -> None:
        source = Path("scripts/preflight_fmp_ohlcv_operations.py").read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", source)
        self.assertNotIn("APIRouter", source)
        self.assertNotIn("scheduler", source.lower())
        self.assertNotIn("migration", source.lower())
        self.assertNotIn("schema", source.lower())
