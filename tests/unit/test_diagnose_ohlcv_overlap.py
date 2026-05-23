from __future__ import annotations

import os
import unittest
from datetime import date, datetime, timezone
from unittest.mock import Mock, patch


class DiagnoseOhlcvOverlapTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.diagnose_ohlcv_overlap as mod

        return mod

    def test_overlap_grouping_and_safe_output(self) -> None:
        mod = self._module()
        connection = Mock()
        result = Mock()
        result.fetchall.return_value = [
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 2, tzinfo=timezone.utc), "timeframe": "1d", "source": "FMP", "adjusted": False},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 2, tzinfo=timezone.utc), "timeframe": "1d", "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 3, tzinfo=timezone.utc), "timeframe": "1d", "source": "polygon_aggregates", "adjusted": True},
        ]
        connection.execute.return_value = result

        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection) as open_connection, patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_ohlcv_overlap.py",
                "--symbol",
                "SPY",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
                "--timeframe",
                "1d",
            ],
        ):
            exit_code = mod.main()

        self.assertEqual(exit_code, 0)
        open_connection.assert_called_once()
        sql, params = connection.execute.call_args.args
        self.assertIn("FROM canonical_ohlcv", sql)
        self.assertEqual(params, ("SPY", date(2025, 1, 2), date(2025, 1, 10), "1d"))
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("total_rows=3", printed)
        self.assertIn("unique_timestamp_count=2", printed)
        self.assertIn("duplicate_timestamp_groups=1", printed)
        self.assertIn("per_source_row_counts={FMP=1, polygon_aggregates=2}", printed)
        self.assertIn("per_adjusted_row_counts={False=1, True=2}", printed)
        self.assertIn("sample_duplicate_group_1 timestamp=2025-01-02T00:00:00+00:00 count=2", printed)
        self.assertNotIn("DATABASE_URL", printed)

    def test_requires_database_url_and_not_vendor_key(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "sys.argv",
            [
                "diagnose_ohlcv_overlap.py",
                "--symbol",
                "SPY",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
            ],
        ):
            with self.assertRaises(RuntimeError):
                mod.main()

    def test_zero_rows_prints_safely(self) -> None:
        mod = self._module()
        connection = Mock()
        result = Mock()
        result.fetchall.return_value = []
        connection.execute.return_value = result

        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_ohlcv_overlap.py",
                "--symbol",
                "SPY",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("total_rows=0", printed)
        self.assertIn("unique_timestamp_count=0", printed)
        self.assertIn("duplicate_timestamp_groups=0", printed)
        self.assertNotIn("sample_duplicate_group_1", printed)

    def test_sample_output_is_capped(self) -> None:
        mod = self._module()
        connection = Mock()
        rows = []
        for day in range(1, 8):
            rows.append({"symbol": "SPY", "timestamp": datetime(2025, 1, day, tzinfo=timezone.utc), "timeframe": "1d", "source": "FMP", "adjusted": False})
            rows.append({"symbol": "SPY", "timestamp": datetime(2025, 1, day, tzinfo=timezone.utc), "timeframe": "1d", "source": "polygon_aggregates", "adjusted": True})
        result = Mock()
        result.fetchall.return_value = rows
        connection.execute.return_value = result

        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_ohlcv_overlap.py",
                "--symbol",
                "SPY",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
            ],
        ):
            mod.main()

        printed_lines = [" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls]
        sample_lines = [line for line in printed_lines if line.startswith("sample_duplicate_group_")]
        self.assertEqual(len(sample_lines), 5)
        self.assertTrue(any("sample_duplicate_groups_truncated=2" in line for line in printed_lines))

    def test_no_db_writes(self) -> None:
        mod = self._module()
        connection = Mock()
        result = Mock()
        result.fetchall.return_value = []
        connection.execute.return_value = result

        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch(
            "sys.argv",
            [
                "diagnose_ohlcv_overlap.py",
                "--symbol",
                "SPY",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
            ],
        ):
            mod.main()

        connection.commit.assert_not_called()
        connection.rollback.assert_not_called()
