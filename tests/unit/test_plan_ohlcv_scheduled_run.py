from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest.mock import patch


class PlanOhlcvScheduledRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.plan_ohlcv_scheduled_run as mod

        return mod

    def test_fmp_daily_schedule_plan_can_be_generated(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "plan_ohlcv_scheduled_run.py",
                "--vendor",
                "fmp",
                "--symbol",
                "AAPL",
                "--as-of-date",
                "2026-01-14",
                "--confirm-write",
                "--record-run",
                "--record-quality",
                "--record-lineage",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("vendor=fmp", printed)
        self.assertIn("selected_symbols=('AAPL',)", printed)
        self.assertIn("schedule_allowed=false", printed)
        self.assertIn("python -m scripts.run_fmp_ohlcv_daily_update", printed)
        self.assertIn("python -m scripts.preflight_fmp_ohlcv_operations", printed)
        self.assertIn("python -m scripts.verify_fmp_ohlcv_evidence_chain", printed)
        self.assertIn("--confirm-write", printed)
        self.assertIn("FMP_API_KEY", printed)
        self.assertIn("DATABASE_URL", printed)

    def test_polygon_backfill_schedule_plan_is_blocked_manual_only(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "plan_ohlcv_scheduled_run.py",
                "--vendor",
                "polygon",
                "--symbol",
                "SPY",
                "--start-date",
                "2026-01-10",
                "--end-date",
                "2026-01-14",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("vendor=polygon", printed)
        self.assertIn("selected_symbols=('SPY',)", printed)
        self.assertIn("schedule_allowed=false", printed)
        self.assertIn("polygon_backfill_remains_manual_only", printed)
        self.assertIn("python -m scripts.run_polygon_ohlcv_chunked_backfill", printed)
        self.assertIn("python -m scripts.preflight_polygon_ohlcv_operations", printed)
        self.assertIn("python -m scripts.verify_polygon_ohlcv_evidence_chain", printed)

    def test_source_has_no_scheduler_api_or_migration_imports(self) -> None:
        source = Path("scripts/plan_ohlcv_scheduled_run.py").read_text(encoding="utf-8")
        self.assertNotIn("from fastapi", source.lower())
        self.assertNotIn("apirouter", source.lower())
        self.assertNotIn("alembic", source.lower())
        self.assertNotIn("ai_market_machine_data", source)
        self.assertNotIn("from app.api", source)
        self.assertNotIn("import app.api", source)

    def test_no_vendor_calls_or_db_writes(self) -> None:
        mod = self._module()
        report = mod.build_scheduler_plan(
            mod.argparse.Namespace(
                vendor="fmp",
                symbol=["AAPL"],
                as_of_date="2026-01-14",
                start_date=None,
                end_date=None,
                timeframe="1d",
                confirm_write=False,
                record_run=False,
                record_quality=False,
                record_lineage=False,
            )
        )
        self.assertEqual(report.vendor, "fmp")
        self.assertFalse(report.schedule_allowed)
        self.assertIn("--dry-run", report.intended_command)

    def test_docs_include_boundary_constraints(self) -> None:
        text = Path("docs/ohlcv_scheduler_contract.md").read_text(encoding="utf-8")
        self.assertIn("scheduler contract", text.lower())
        self.assertIn("polygon backfill remains manual", text.lower())
        self.assertIn("schedule_allowed=false", text)
