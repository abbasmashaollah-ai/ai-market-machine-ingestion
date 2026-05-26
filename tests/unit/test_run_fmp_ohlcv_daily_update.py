from __future__ import annotations

import os
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch


class RunFmpOhlcvDailyUpdateTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.run_fmp_ohlcv_daily_update as mod

        return mod

    def test_default_runner_is_dry_run_and_emits_batch_payload(self) -> None:
        mod = self._module()
        fake_result = SimpleNamespace(
            vendor="fmp",
            requested_symbols=("AAPL", "MSFT"),
            completed_symbols=("AAPL", "MSFT"),
            failed_symbols=(),
            raw_record_count=2,
            normalized_record_count=2,
            writer_status="not_requested",
            checkpoint_status="not_requested",
            did_write_db=False,
            batch_errors=(),
            per_symbol_results=({"symbol": "AAPL"}, {"symbol": "MSFT"}),
        )
        with patch.object(mod, "build_multi_symbol_ohlcv_fanout", return_value=fake_result) as build_mock, patch(
            "builtins.print"
        ) as print_mock, patch.object(mod, "_open_connection") as open_connection_mock, patch(
            "sys.argv",
            ["run_fmp_ohlcv_daily_update.py", "--symbol", "AAPL", "--symbol", "MSFT", "--as-of-date", "2026-01-14"],
        ):
            mod.main()

        self.assertEqual(build_mock.call_count, 1)
        self.assertFalse(build_mock.call_args.kwargs["execute_writer"])
        self.assertFalse(build_mock.call_args.kwargs["execute_checkpoint_persistence"])
        open_connection_mock.assert_not_called()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("run_type=manual_fmp_daily_ohlcv", printed)
        self.assertIn("vendor=fmp", printed)
        self.assertIn("did_write_db=False", printed)
        self.assertIn("requested_symbols=('AAPL', 'MSFT')", printed)
        self.assertIn("dry_run=True", printed)

    def test_confirm_write_enables_writer_execution(self) -> None:
        mod = self._module()
        fake_result = SimpleNamespace(
            vendor="fmp",
            requested_symbols=("AAPL",),
            completed_symbols=("AAPL",),
            failed_symbols=(),
            raw_record_count=1,
            normalized_record_count=1,
            writer_status="completed",
            checkpoint_status="not_requested",
            did_write_db=True,
            batch_errors=(),
            per_symbol_results=({"symbol": "AAPL", "status": "completed", "did_write_db": True},),
        )
        fake_connection = Mock()
        with patch.dict(
            os.environ,
            {"DATABASE_URL": "postgresql://user:pass@host/db"},
            clear=True,
        ), patch.object(mod, "load_local_env_if_available", return_value=False), patch.object(
            mod, "_open_connection", return_value=fake_connection
        ) as open_connection_mock, patch.object(mod, "OhlcvWriter") as writer_cls, patch.object(
            mod, "IngestionRunStore"
        ) as run_store_cls, patch.object(mod, "DataQualityResultStore"), patch.object(
            mod, "DataLineageStore"
        ), patch.object(mod, "build_multi_symbol_ohlcv_fanout", return_value=fake_result) as build_mock, patch(
            "builtins.print"
        ), patch(
            "sys.argv",
            ["run_fmp_ohlcv_daily_update.py", "--symbol", "AAPL", "--as-of-date", "2026-01-14", "--confirm-write"],
        ):
            mod.main()

        open_connection_mock.assert_called_once()
        writer_cls.assert_called_once_with(fake_connection)
        run_store_cls.assert_not_called()
        self.assertTrue(build_mock.call_args.kwargs["execute_writer"])
        self.assertIs(build_mock.call_args.kwargs["writer"], writer_cls.return_value)
        self.assertFalse(build_mock.call_args.kwargs["execute_checkpoint_persistence"])

    def test_explicit_dry_run_keeps_writer_disabled(self) -> None:
        mod = self._module()
        fake_result = SimpleNamespace(
            vendor="fmp",
            requested_symbols=("AAPL",),
            completed_symbols=("AAPL",),
            failed_symbols=(),
            raw_record_count=1,
            normalized_record_count=1,
            writer_status="not_requested",
            checkpoint_status="not_requested",
            did_write_db=False,
            batch_errors=(),
            per_symbol_results=(),
        )
        with patch.dict(
            os.environ,
            {"DATABASE_URL": "postgresql://user:pass@host/db"},
            clear=True,
        ), patch.object(mod, "load_local_env_if_available", return_value=False), patch.object(
            mod, "build_multi_symbol_ohlcv_fanout", return_value=fake_result
        ) as build_mock, patch.object(mod, "_open_connection") as open_connection_mock, patch(
            "builtins.print"
        ), patch(
            "sys.argv",
            ["run_fmp_ohlcv_daily_update.py", "--symbol", "AAPL", "--as-of-date", "2026-01-14", "--dry-run"],
        ):
            mod.main()

        self.assertFalse(build_mock.call_args.kwargs["execute_writer"])
        open_connection_mock.assert_not_called()

    def test_record_flags_persist_run_quality_and_lineage(self) -> None:
        mod = self._module()
        fake_result = SimpleNamespace(
            vendor="fmp",
            requested_symbols=("AAPL",),
            completed_symbols=("AAPL",),
            failed_symbols=(),
            raw_record_count=1,
            normalized_record_count=1,
            writer_status="not_requested",
            checkpoint_status="not_requested",
            did_write_db=True,
            batch_errors=(),
            per_symbol_results=(
                {"symbol": "AAPL", "status": "completed", "raw_record_count": 1, "normalized_record_count": 1, "did_write_db": True, "writer_status": "completed"},
            ),
        )
        fake_connection = Mock()
        run_store = Mock()
        quality_store = Mock()
        lineage_store = Mock()
        with patch.dict(
            os.environ,
            {"DATABASE_URL": "postgresql://user:pass@host/db"},
            clear=True,
        ), patch.object(mod, "load_local_env_if_available", return_value=False), patch.object(
            mod, "_open_connection", return_value=fake_connection
        ) as open_connection_mock, patch.object(mod, "OhlcvWriter") as writer_cls, patch.object(
            mod, "IngestionRunStore", return_value=run_store
        ) as run_store_cls, patch.object(mod, "DataQualityResultStore", return_value=quality_store) as quality_store_cls, patch.object(
            mod, "DataLineageStore", return_value=lineage_store
        ) as lineage_store_cls, patch.object(
            mod, "build_multi_symbol_ohlcv_fanout", return_value=fake_result
        ) as build_mock, patch(
            "builtins.print"
        ), patch(
            "sys.argv",
            [
                "run_fmp_ohlcv_daily_update.py",
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

        open_connection_mock.assert_called_once()
        writer_cls.assert_called_once_with(fake_connection)
        run_store_cls.assert_called_once_with(fake_connection)
        quality_store_cls.assert_called_once_with(fake_connection)
        lineage_store_cls.assert_called_once_with(fake_connection)
        self.assertTrue(build_mock.call_args.kwargs["execute_writer"])
        run_store.save_run.assert_called_once()
        quality_store.save_validation_results.assert_called_once()
        lineage_store.save_chunk_lineage.assert_called_once()

    def test_max_symbols_is_enforced(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch(
            "sys.argv",
            [
                "run_fmp_ohlcv_daily_update.py",
                "--symbol",
                "AAPL",
                "--symbol",
                "MSFT",
                "--symbol",
                "SPY",
                "--symbol",
                "QQQ",
                "--as-of-date",
                "2026-01-14",
            ],
        ):
            with self.assertRaises(RuntimeError):
                mod.main()

    def test_symbol_and_date_arguments_are_passed_to_fanout(self) -> None:
        mod = self._module()
        fake_result = SimpleNamespace(
            vendor="fmp",
            requested_symbols=("AAPL", "MSFT"),
            completed_symbols=("AAPL",),
            failed_symbols=("MSFT",),
            raw_record_count=1,
            normalized_record_count=1,
            writer_status="failed",
            checkpoint_status="not_requested",
            did_write_db=False,
            batch_errors=({"kind": "symbol_orchestrator_error"},),
            per_symbol_results=(),
        )
        with patch.object(mod, "build_multi_symbol_ohlcv_fanout", return_value=fake_result) as build_mock, patch(
            "builtins.print"
        ), patch(
            "sys.argv",
            [
                "run_fmp_ohlcv_daily_update.py",
                "--symbol",
                "AAPL",
                "--symbol",
                "MSFT",
                "--start-date",
                "2026-01-10",
                "--end-date",
                "2026-01-14",
            ],
        ):
            mod.main()

        request = build_mock.call_args.args[0]
        self.assertEqual(request.symbols, ("AAPL", "MSFT"))
        self.assertEqual(request.start_date, date(2026, 1, 10))
        self.assertEqual(request.end_date, date(2026, 1, 14))

    def test_fail_fast_passes_through(self) -> None:
        mod = self._module()
        fake_result = SimpleNamespace(
            vendor="fmp",
            requested_symbols=("AAPL",),
            completed_symbols=("AAPL",),
            failed_symbols=(),
            raw_record_count=1,
            normalized_record_count=1,
            writer_status="not_requested",
            checkpoint_status="not_requested",
            did_write_db=False,
            batch_errors=(),
            per_symbol_results=(),
        )
        with patch.object(mod, "build_multi_symbol_ohlcv_fanout", return_value=fake_result) as build_mock, patch(
            "builtins.print"
        ), patch("sys.argv", ["run_fmp_ohlcv_daily_update.py", "--as-of-date", "2026-01-14", "--fail-fast"]):
            mod.main()

        self.assertTrue(build_mock.call_args.kwargs["fail_fast"])

    def test_deprecated_per_symbol_results_are_not_counted_as_success(self) -> None:
        mod = self._module()
        fake_result = SimpleNamespace(
            vendor="fmp",
            requested_symbols=("AAPL", "MSFT"),
            completed_symbols=("AAPL",),
            failed_symbols=("MSFT",),
            raw_record_count=1,
            normalized_record_count=1,
            writer_status="failed",
            checkpoint_status="not_requested",
            did_write_db=False,
            batch_errors=({"kind": "symbol_orchestrator_error", "symbol": "MSFT"},),
            per_symbol_results=(
                {"symbol": "AAPL", "status": "completed"},
                {"symbol": "MSFT", "status": "failed"},
            ),
        )
        with patch.object(mod, "build_multi_symbol_ohlcv_fanout", return_value=fake_result), patch(
            "builtins.print"
        ) as print_mock, patch(
            "sys.argv",
            ["run_fmp_ohlcv_daily_update.py", "--symbol", "AAPL", "--symbol", "MSFT", "--as-of-date", "2026-01-14"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("completed_symbols=('AAPL',)", printed)
        self.assertIn("failed_symbols=('MSFT',)", printed)

    def test_source_boundary_has_no_data_repo_imports(self) -> None:
        source = Path("scripts/run_fmp_ohlcv_daily_update.py").read_text(encoding="utf-8")
        self.assertNotIn("ai-market-machine-data", source)
        self.assertNotIn("ai_market_machine_data", source)
        self.assertNotIn("FastAPI", source)
        self.assertNotIn("APIRouter", source)
        self.assertNotIn("alembic", source.lower())
        self.assertNotIn("scheduler", source.lower())
        self.assertNotIn("migration", source.lower())
        self.assertNotIn("schema", source.lower())
