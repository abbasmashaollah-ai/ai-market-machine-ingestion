from __future__ import annotations

import os
import unittest
from datetime import date, datetime, timezone
from unittest.mock import Mock, patch


class DiagnoseOhlcvCoverageTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.diagnose_ohlcv_coverage as mod

        return mod

    def test_expected_weekday_calculation(self) -> None:
        mod = self._module()
        days = mod._expected_weekdays(date(2025, 1, 2), date(2025, 1, 10))
        self.assertEqual([day.isoformat() for day in days], ["2025-01-02", "2025-01-03", "2025-01-06", "2025-01-07", "2025-01-08", "2025-01-10"])

    def test_full_coverage(self) -> None:
        mod = self._module()
        connection = Mock()
        result = Mock()
        result.fetchall.return_value = [
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 2, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 3, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 6, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 7, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 8, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 9, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 10, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
        ]
        connection.execute.return_value = result

        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db"}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch.object(
            mod, "_open_connection", return_value=connection
        ), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_ohlcv_coverage.py",
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
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("expected_weekdays=6", printed)
        self.assertIn("missing_weekdays=[]", printed)
        self.assertIn("coverage_ratio=1.000", printed)
        self.assertIn("source_filter=None", printed)

    def test_missing_weekday_detection(self) -> None:
        mod = self._module()
        connection = Mock()
        result = Mock()
        result.fetchall.return_value = [
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 2, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 3, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 7, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
        ]
        connection.execute.return_value = result

        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db"}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch.object(
            mod, "_open_connection", return_value=connection
        ), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_ohlcv_coverage.py",
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
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("missing_weekdays=[2025-01-06, 2025-01-08, 2025-01-10]", printed)
        self.assertIn("coverage_ratio=0.500", printed)

    def test_source_filtered_coverage(self) -> None:
        mod = self._module()
        connection = Mock()
        result = Mock()
        result.fetchall.return_value = [
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 2, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 3, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
        ]
        connection.execute.return_value = result

        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db"}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch.object(
            mod, "_open_connection", return_value=connection
        ), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_ohlcv_coverage.py",
                "--symbol",
                "SPY",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
                "--timeframe",
                "1d",
                "--source",
                "polygon_aggregates",
            ],
        ):
            mod.main()

        sql, params = connection.execute.call_args.args
        self.assertIn("AND source = %s", sql)
        self.assertEqual(params, ("SPY", date(2025, 1, 2), date(2025, 1, 11), "1d", "polygon_aggregates"))
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("source_filter=polygon_aggregates", printed)
        self.assertIn("sources=['polygon_aggregates']", printed)

    def test_zero_rows_and_weekend_exclusion(self) -> None:
        mod = self._module()
        self.assertEqual(mod._expected_weekdays(date(2025, 1, 4), date(2025, 1, 5)), [])
        connection = Mock()
        result = Mock()
        result.fetchall.return_value = []
        connection.execute.return_value = result

        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db"}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch.object(
            mod, "_open_connection", return_value=connection
        ), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_ohlcv_coverage.py",
                "--symbol",
                "SPY",
                "--start-date",
                "2025-01-04",
                "--end-date",
                "2025-01-05",
                "--timeframe",
                "1d",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("expected_weekdays=0", printed)
        self.assertIn("coverage_ratio=0.000", printed)
        self.assertIn("missing_weekdays=[]", printed)

    def test_capped_missing_sample_output(self) -> None:
        mod = self._module()
        connection = Mock()
        result = Mock()
        result.fetchall.return_value = [
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 2, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
        ]
        connection.execute.return_value = result

        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db"}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch.object(
            mod, "_open_connection", return_value=connection
        ), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "diagnose_ohlcv_coverage.py",
                "--symbol",
                "SPY",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-14",
                "--timeframe",
                "1d",
            ],
        ):
            mod.main()

        printed_lines = [" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls]
        sample_lines = [line for line in printed_lines if line.startswith("sample_missing_date_")]
        self.assertEqual(len(sample_lines), 5)
        self.assertTrue(any("sample_missing_dates_truncated=" in line for line in printed_lines))

    def test_requires_database_url_and_not_polygon_key(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "sys.argv",
            [
                "diagnose_ohlcv_coverage.py",
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

    def test_no_db_writes_and_no_vendor_calls(self) -> None:
        mod = self._module()
        connection = Mock()
        result = Mock()
        result.fetchall.return_value = []
        connection.execute.return_value = result

        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db"}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch.object(
            mod, "_open_connection", return_value=connection
        ), patch(
            "sys.argv",
            [
                "diagnose_ohlcv_coverage.py",
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
