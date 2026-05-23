from __future__ import annotations

import os
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import Mock, patch


class PreflightPolygonOhlcvOperationsTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.preflight_polygon_ohlcv_operations as mod

        return mod

    @staticmethod
    def _fake_connection(rows_by_sql_fragment: dict[str, list[dict[str, object]]]) -> Mock:
        connection = Mock()

        def execute(sql: str, params: tuple[object, ...]) -> Mock:
            result = Mock()
            rows = []
            for fragment, value in rows_by_sql_fragment.items():
                if fragment in sql:
                    rows = value
                    break
            result.fetchall.return_value = rows
            return result

        connection.execute.side_effect = execute
        return connection

    def test_default_symbols(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            ["preflight_polygon_ohlcv_operations.py", "--as-of-date", "2025-01-14"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("symbol=SPY", printed)
        self.assertIn("symbol=QQQ", printed)
        self.assertIn("symbol=IWM", printed)

    def test_repeated_symbol_override(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            [
                "preflight_polygon_ohlcv_operations.py",
                "--symbol",
                "SPY",
                "--symbol",
                "QQQ",
                "--as-of-date",
                "2025-01-14",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("symbols_total=2", printed)

    def test_universe_cap(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            [
                "preflight_polygon_ohlcv_operations.py",
                "--symbol",
                "SPY",
                "--symbol",
                "QQQ",
                "--symbol",
                "IWM",
                "--as-of-date",
                "2025-01-14",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("symbols_total=3", printed)

    def test_db_unavailable_without_check_existing(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "builtins.print"
        ), patch(
            "sys.argv",
            ["preflight_polygon_ohlcv_operations.py", "--symbol", "SPY", "--as-of-date", "2025-01-14"],
        ):
            mod.main()

    def test_db_required_with_check_existing(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "sys.argv",
            ["preflight_polygon_ohlcv_operations.py", "--symbol", "SPY", "--as-of-date", "2025-01-14", "--check-existing"],
        ):
            with self.assertRaises(RuntimeError):
                mod.main()

    def test_evidence_complete_case(self) -> None:
        mod = self._module()
        fake_connection = self._fake_connection(
            {
                "FROM canonical_ohlcv": [{"timestamp": date(2025, 1, 14), "source": "polygon_aggregates"}],
                "FROM ingestion_runs": [{"status": "success"}],
                "FROM data_quality_results": [{"status": "pass"}],
                "FROM data_lineage": [{"quality_status": "pass"}],
            }
        )
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=fake_connection), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            ["preflight_polygon_ohlcv_operations.py", "--symbol", "SPY", "--as-of-date", "2025-01-14", "--check-existing"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("evidence_status=complete", printed)
        self.assertIn("recommended_command=None", printed)

    def test_evidence_missing_or_partial_case(self) -> None:
        mod = self._module()
        fake_connection = self._fake_connection(
            {
                "FROM canonical_ohlcv": [{"timestamp": date(2025, 1, 14), "source": "polygon_aggregates"}],
                "FROM ingestion_runs": [],
                "FROM data_quality_results": [{"status": "pass"}],
                "FROM data_lineage": [],
            }
        )
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=fake_connection), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            ["preflight_polygon_ohlcv_operations.py", "--symbol", "SPY", "--as-of-date", "2025-01-14", "--check-existing"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("evidence_status=partial", printed)
        self.assertIn("recommended_command=python -m scripts.verify_polygon_ohlcv_evidence_chain", printed)

    def test_request_budget_blocked(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            [
                "preflight_polygon_ohlcv_operations.py",
                "--symbol",
                "SPY",
                "--symbol",
                "QQQ",
                "--as-of-date",
                "2025-01-14",
                "--max-requests",
                "1",
            ],
        ):
            mod.main()

        self.assertTrue(any("request_budget_status=exceeds_budget" in " ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls))
        self.assertTrue(any("preflight_status=blocked" in " ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls))
        self.assertTrue(any("recommended_next_step=reduce_scope_or_raise_budget" in " ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls))

    def test_recommended_action_generation(self) -> None:
        mod = self._module()
        fake_connection = self._fake_connection(
            {
                "FROM canonical_ohlcv": [{"timestamp": date(2025, 1, 13), "source": "polygon_aggregates"}],
                "FROM ingestion_runs": [{"status": "success"}],
                "FROM data_quality_results": [],
                "FROM data_lineage": [],
            }
        )
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=fake_connection), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            ["preflight_polygon_ohlcv_operations.py", "--symbol", "SPY", "--as-of-date", "2025-01-14", "--check-existing"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("recommended_action=run_daily_update", printed)
        self.assertIn("recommended_command=python -m scripts.run_polygon_ohlcv_daily_update", printed)

    def test_up_to_date_no_action(self) -> None:
        mod = self._module()
        fake_connection = self._fake_connection(
            {
                "FROM canonical_ohlcv": [{"timestamp": date(2025, 1, 14), "source": "polygon_aggregates"}],
                "FROM ingestion_runs": [{"status": "success"}],
                "FROM data_quality_results": [{"status": "pass"}],
                "FROM data_lineage": [{"quality_status": "pass"}],
            }
        )
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=fake_connection), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            ["preflight_polygon_ohlcv_operations.py", "--symbol", "SPY", "--as-of-date", "2025-01-14", "--check-existing"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("recommended_action=no_action_needed", printed)
        self.assertIn("recommended_command=None", printed)

    def test_no_existing_data_conservative_command(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            ["preflight_polygon_ohlcv_operations.py", "--symbol", "SPY", "--as-of-date", "2025-01-14"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("recommended_action=run_small_backfill_or_daily_update", printed)
        self.assertIn("python -m scripts.run_polygon_ohlcv_daily_update", printed)
        self.assertNotIn("--confirm-write", printed)

    def test_command_has_no_secrets(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            ["preflight_polygon_ohlcv_operations.py", "--symbol", "SPY", "--as-of-date", "2025-01-14"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertNotIn("DATABASE_URL", printed)
        self.assertNotIn("POLYGON_API_KEY", printed)

    def test_no_vendor_calls_and_no_db_writes(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch.object(
            mod, "_open_connection"
        ) as open_connection_mock, patch(
            "builtins.print"
        ), patch(
            "sys.argv",
            ["preflight_polygon_ohlcv_operations.py", "--symbol", "SPY", "--as-of-date", "2025-01-14"],
        ):
            mod.main()

        open_connection_mock.assert_not_called()

    def test_source_has_no_schema_migration_scheduler_api_ai_behavior(self) -> None:
        source = Path(__file__).resolve().parents[2] / "scripts" / "preflight_polygon_ohlcv_operations.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("migration", text.lower())
        self.assertNotIn("strategy", text.lower())
        self.assertNotIn("prediction", text.lower())
