from __future__ import annotations

import os
import unittest
from unittest.mock import patch


class CheckManualFredPersistenceReadinessTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.check_manual_fred_persistence_readiness as mod

        return mod

    def test_no_env_vars_present(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch("builtins.print") as print_mock:
            exit_code = mod.main()

        self.assertEqual(exit_code, 0)
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("dry_run_ready=false", printed)
        self.assertIn("confirmed_write_ready=false", printed)
        self.assertIn("FRED_API_KEY", printed)
        self.assertIn("DATABASE_URL", printed)

    def test_only_fred_api_key_present(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"FRED_API_KEY": "fred-secret"}, clear=True), patch("builtins.print") as print_mock:
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("dry_run_ready=true", printed)
        self.assertIn("confirmed_write_ready=false", printed)
        self.assertIn("DATABASE_URL", printed)
        self.assertNotIn("fred-secret", printed)

    def test_both_env_vars_present(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"FRED_API_KEY": "fred-secret", "DATABASE_URL": "postgresql://example/db"}, clear=True), patch(
            "builtins.print"
        ) as print_mock:
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("dry_run_ready=true", printed)
        self.assertIn("confirmed_write_ready=true", printed)
        self.assertIn("missing=[]", printed)
        self.assertNotIn("fred-secret", printed)
        self.assertNotIn("postgresql://example/db", printed)

    def test_no_vendor_calls_no_db_connections(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"FRED_API_KEY": "fred-secret", "DATABASE_URL": "postgresql://example/db"}, clear=True), patch(
            "builtins.print"
        ), patch.object(mod, "_validate_database_url", wraps=mod._validate_database_url) as validate_mock:
            mod.main()

        validate_mock.assert_called_once()

    def test_safe_command_import_behavior(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "_import_manual_commands", wraps=mod._import_manual_commands) as import_mock:
            mod.main()

        import_mock.assert_called_once()
