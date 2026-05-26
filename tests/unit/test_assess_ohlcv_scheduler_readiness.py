from __future__ import annotations

import ast
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


class AssessOhlcvSchedulerReadinessTests(unittest.TestCase):
    def _module(self):
        import scripts.assess_ohlcv_scheduler_readiness as mod

        return mod

    @staticmethod
    def _ready_summary() -> tuple[list[dict[str, object]], dict[str, object]]:
        return [], {"preflight_status": "ready"}

    def test_pass_when_manual_foundations_exist(self) -> None:
        mod = self._module()
        def ready_preflight(*_: object, **__: object) -> tuple[str, str, dict[str, object]]:
            return "PASS", "ready", {"preflight_status": "ready"}

        with patch.object(mod, "_run_preflight", side_effect=ready_preflight), patch("builtins.print") as print_mock:
            report = mod.build_scheduler_readiness_report()
            exit_code = mod.main()

        self.assertEqual(exit_code, 0)
        self.assertEqual(report["scheduler_readiness_status"], "PASS")
        self.assertEqual(report["blockers"], ())
        self.assertEqual(report["next_required_step"], "none")
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("scheduler_readiness_status=PASS", printed)
        self.assertIn("manual_inventory_status=PASS", printed)
        self.assertIn("fmp_preflight_status=PASS", printed)
        self.assertIn("polygon_preflight_status=PASS", printed)

    def test_warn_when_optional_docs_or_evidence_tools_missing(self) -> None:
        mod = self._module()

        def fake_exists(path: Path) -> bool:
            missing = {
                Path("docs/fmp_ohlcv_evidence_chain_verification.md"),
                Path("tests/unit/test_writer_contracts.py"),
                Path("scripts/start_scheduler.py"),
                Path("app/scheduler/scheduler.py"),
            }
            return path not in missing

        with patch.object(mod, "_run_preflight", side_effect=[("PASS", "ready", {"preflight_status": "ready"}), ("PASS", "ready", {"preflight_status": "ready"})]), patch.object(
            mod, "_exists", side_effect=fake_exists
        ):
            report = mod.build_scheduler_readiness_report()

        self.assertEqual(report["scheduler_readiness_status"], "WARN")
        self.assertEqual(report["blockers"], ())
        self.assertTrue(any(item.startswith("missing_optional_doc:") or item.startswith("missing_optional_test:") for item in report["warnings"]))

    def test_fail_when_scheduler_activation_files_exist_too_early(self) -> None:
        mod = self._module()

        def fake_exists(path: Path) -> bool:
            if path in {Path("scripts/start_scheduler.py"), Path("app/scheduler/scheduler.py")}:
                return True
            return True

        with patch.object(mod, "_run_preflight", side_effect=[("PASS", "ready", {"preflight_status": "ready"}), ("PASS", "ready", {"preflight_status": "ready"})]), patch.object(
            mod, "_exists", side_effect=fake_exists
        ):
            report = mod.build_scheduler_readiness_report()

        self.assertEqual(report["scheduler_readiness_status"], "FAIL")
        self.assertIn("scheduler_activation_files_exist_too_early", report["blockers"])

    def test_fail_when_manual_command_inventory_incomplete(self) -> None:
        mod = self._module()
        with patch.object(mod, "MANUAL_COMMAND_MODULES", ()), patch.object(
            mod, "_run_preflight", side_effect=[("PASS", "ready", {"preflight_status": "ready"}), ("PASS", "ready", {"preflight_status": "ready"})]
        ):
            report = mod.build_scheduler_readiness_report()

        self.assertEqual(report["scheduler_readiness_status"], "FAIL")
        self.assertIn("manual_command_inventory_incomplete", report["blockers"])

    def test_fail_when_forbidden_imports_are_detected(self) -> None:
        mod = self._module()
        with patch.object(mod, "_manual_command_imports_are_safe", return_value=["scripts/run_fmp_ohlcv_daily_update.py:FastAPI"]), patch.object(
            mod, "_run_preflight", side_effect=[("PASS", "ready", {"preflight_status": "ready"}), ("PASS", "ready", {"preflight_status": "ready"})]
        ):
            report = mod.build_scheduler_readiness_report()

        self.assertEqual(report["scheduler_readiness_status"], "FAIL")
        self.assertIn("forbidden_imports_in_manual_commands", report["blockers"])

    def test_source_has_no_forbidden_activation_or_api_imports(self) -> None:
        source = Path("scripts/assess_ohlcv_scheduler_readiness.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported_modules: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.add(node.module)

        forbidden_modules = {
            "fastapi",
            "alembic",
            "ai_market_machine_data",
        }
        self.assertTrue(forbidden_modules.isdisjoint({module.split(".")[0] for module in imported_modules}))
