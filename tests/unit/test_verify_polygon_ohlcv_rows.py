from __future__ import annotations

import os
import unittest
from datetime import date, datetime, timezone
from unittest.mock import Mock, patch


class VerifyPolygonOhlcvRowsTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.verify_polygon_ohlcv_rows as mod

        return mod

    def test_query_shape_and_safe_output(self) -> None:
        mod = self._module()
        connection = Mock()
        result = Mock()
        result.fetchall.return_value = [
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 2, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 3, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
        ]
        connection.execute.return_value = result

        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection) as open_connection, patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "verify_polygon_ohlcv_rows.py",
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
        self.assertIn("row_count=2", printed)
        self.assertIn("first_timestamp=2025-01-02T00:00:00+00:00", printed)
        self.assertIn("last_timestamp=2025-01-03T00:00:00+00:00", printed)
        self.assertIn("adjusted_values=[True]", printed)
        self.assertIn("sources=['polygon_aggregates']", printed)
        self.assertNotIn("DATABASE_URL", printed)

    def test_requires_database_url_and_not_polygon_key(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "sys.argv",
            [
                "verify_polygon_ohlcv_rows.py",
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
                "verify_polygon_ohlcv_rows.py",
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
        self.assertIn("row_count=0", printed)
        self.assertIn("first_timestamp=None", printed)
        self.assertIn("last_timestamp=None", printed)

    def test_no_vendor_calls_or_db_writes(self) -> None:
        mod = self._module()
        connection = Mock()
        result = Mock()
        result.fetchall.return_value = []
        connection.execute.return_value = result

        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch(
            "scripts.verify_polygon_ohlcv_rows._fetch_all",
            wraps=mod._fetch_all,
        ) as fetch_mock, patch(
            "sys.argv",
            [
                "verify_polygon_ohlcv_rows.py",
                "--symbol",
                "SPY",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-10",
            ],
        ):
            mod.main()

        fetch_mock.assert_called_once()
        connection.commit.assert_not_called()
        connection.rollback.assert_not_called()
