from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest.mock import patch


class EventCalendarPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.preflight_event_calendar_operations as mod

        return mod

    def test_preflight_pass(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            exit_code = mod.main([])

        self.assertEqual(exit_code, 0)
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("dry_run_command_exists=True", printed)
        self.assertIn("source_plan_command_exists=True", printed)
        self.assertIn("foundation_doc_exists=True", printed)
        self.assertIn("source_plan_doc_exists=True", printed)
        self.assertIn("normalization_module_exists=True", printed)
        self.assertIn("macro_event_dry_run_command_exists=True", printed)
        self.assertIn("macro_event_source_plan_command_exists=True", printed)
        self.assertIn("macro_event_foundation_doc_exists=True", printed)
        self.assertIn("macro_event_source_plan_doc_exists=True", printed)
        self.assertIn("macro_event_normalization_module_exists=True", printed)
        self.assertIn("starter_event_types_configured=True", printed)
        self.assertIn("macro_event_types_configured=True", printed)
        self.assertIn("forbidden_imports_absent=True", printed)

    def test_no_database_url_requirement(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch("builtins.print") as print_mock:
            mod.main([])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("no_database_url_required_yet=True", printed)

    def test_no_vendor_key_requirement(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch("builtins.print") as print_mock:
            mod.main([])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("no_vendor_api_keys_required_yet=True", printed)

    def test_starter_event_types_present(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main([])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("starter_event_types=['CPI', 'FOMC', 'NFP', 'OPEX', 'earnings_date']", printed)
        self.assertIn("macro_event_types=['CPI', 'FOMC', 'NFP']", printed)

    def test_forbidden_import_guard(self) -> None:
        text = Path("scripts/preflight_event_calendar_operations.py").read_text(encoding="utf-8")
        lowered = text.lower()
        self.assertNotIn("import requests", lowered)
        self.assertNotIn("from requests", lowered)
        self.assertNotIn("import httpx", lowered)
        self.assertNotIn("from httpx", lowered)
        self.assertNotIn("import fastapi", lowered)
        self.assertNotIn("DATABASE_URL", text)

    def test_docs_coverage(self) -> None:
        text = Path("docs/event_calendar_preflight.md").read_text(encoding="utf-8").lower()
        self.assertIn("event calendar preflight", text)
        self.assertIn("dry-run command exists", text)
        self.assertIn("source plan command exists", text)
        self.assertIn("starter event types", text)
        self.assertIn("macro-event dry-run command exists", text)
        self.assertIn("macro-event source plan command exists", text)
        self.assertIn("macro-event foundation doc exists", text)
        self.assertIn("macro-event source plan doc exists", text)
        self.assertIn("cpi/fomc/nfp are configured", text)
        self.assertIn("no db writes", text)
