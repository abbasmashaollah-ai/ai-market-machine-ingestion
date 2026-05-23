from __future__ import annotations

import os
import unittest
from datetime import date, datetime, timezone
from unittest.mock import Mock, patch


class FillPolygonOhlcvGapsTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.fill_polygon_ohlcv_gaps as mod

        return mod

    def _argv(self, *extra: str) -> list[str]:
        return [
            "fill_polygon_ohlcv_gaps.py",
            "--symbol",
            "SPY",
            "--start-date",
            "2025-01-02",
            "--end-date",
            "2025-01-10",
            "--timeframe",
            "1d",
            *extra,
        ]

    def test_detects_missing_weekdays_from_db_coverage(self) -> None:
        mod = self._module()
        connection = Mock()
        result = Mock()
        result.fetchall.return_value = [
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 2, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 3, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
        ]
        connection.execute.return_value = result
        fake_client = Mock()
        fake_client.fetch_aggregates_raw.return_value = []
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db", "POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch.object(mod, "_build_polygon_client", return_value=fake_client), patch(
            "builtins.print"
        ) as print_mock, patch("sys.argv", self._argv()):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("missing_dates_count=5", printed)

    def test_no_gaps_skips_without_vendor_call_if_possible(self) -> None:
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
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch.object(mod, "_build_polygon_client") as client_mock, patch(
            "builtins.print"
        ) as print_mock, patch("sys.argv", self._argv()):
            mod.main()

        client_mock.assert_not_called()
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("status=skipped_no_gaps", printed)

    def test_dry_run_gap_fill_fetches_and_filters_missing_dates_only(self) -> None:
        mod = self._module()
        connection = Mock()
        result = Mock()
        result.fetchall.return_value = [
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 2, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
        ]
        connection.execute.return_value = result
        fake_client = Mock()
        fake_client.fetch_aggregates_raw.return_value = [
            {"ticker": "SPY", "t": 1735776000000, "o": 100, "h": 101, "l": 99, "c": 100.5, "v": 1234, "adjusted": True},
            {"ticker": "SPY", "t": 1735862400000, "o": 101, "h": 102, "l": 100, "c": 101.5, "v": 1234, "adjusted": True},
        ]
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db", "POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch.object(mod, "_build_polygon_client", return_value=fake_client), patch.object(
            mod, "OhlcvWriter"
        ) as writer_cls, patch("builtins.print"), patch("sys.argv", self._argv()):
            mod.main()

        fake_client.fetch_aggregates_raw.assert_called_once()
        writer_cls.assert_not_called()

    def test_confirmed_gap_fill_writes_only_missing_dates_through_writer(self) -> None:
        mod = self._module()
        connection = Mock()
        result = Mock()
        result.fetchall.return_value = [
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 2, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
        ]
        connection.execute.return_value = result
        fake_client = Mock()
        fake_client.fetch_aggregates_raw.return_value = [
            {"ticker": "SPY", "t": 1736121600000, "o": 100, "h": 101, "l": 99, "c": 100.5, "v": 1234, "adjusted": True},
        ]
        writer = Mock()
        writer.write.return_value = type("Result", (), {"written_count": 1, "status": type("Status", (), {"value": "success"})()})()
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db", "POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch.object(mod, "_build_polygon_client", return_value=fake_client), patch.object(
            mod, "OhlcvWriter", return_value=writer
        ), patch("builtins.print"), patch("sys.argv", self._argv("--confirm-write")):
            mod.main()

        writer.write.assert_called_once()
        written_records = writer.write.call_args.args[0]
        self.assertEqual(len(written_records), 1)
        self.assertEqual(written_records[0].source, "polygon_aggregates")
        self.assertEqual(written_records[0].timeframe, "1d")
        self.assertTrue(written_records[0].adjusted)

    def test_polygon_key_required_only_when_gaps_require_fetch(self) -> None:
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
        ), patch.object(mod, "_open_connection", return_value=connection), patch("sys.argv", self._argv()):
            with self.assertRaises(RuntimeError):
                mod.main()

    def test_invalid_fetched_rows_not_written(self) -> None:
        mod = self._module()
        connection = Mock()
        result = Mock()
        result.fetchall.return_value = [
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 2, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
        ]
        connection.execute.return_value = result
        fake_client = Mock()
        fake_client.fetch_aggregates_raw.return_value = [
            {"ticker": "SPY", "t": 1736121600000, "o": 100, "h": 99, "l": 101, "c": 100.5, "v": -1, "adjusted": True},
        ]
        writer = Mock()
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db", "POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch.object(mod, "_build_polygon_client", return_value=fake_client), patch.object(
            mod, "OhlcvWriter", return_value=writer
        ), patch("builtins.print"), patch("sys.argv", self._argv("--confirm-write")):
            mod.main()

        writer.write.assert_not_called()

    def test_partial_fill_status_when_polygon_lacks_one_missing_date(self) -> None:
        mod = self._module()
        connection = Mock()
        first = Mock()
        first.fetchall.return_value = [
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 2, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 3, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 6, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 7, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 8, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
        ]
        second = Mock()
        second.fetchall.return_value = [
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 2, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 3, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 6, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 7, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 8, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 9, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
        ]
        connection.execute.side_effect = [first, second]
        fake_client = Mock()
        fake_client.fetch_aggregates_raw.return_value = [
            {"ticker": "SPY", "t": 1736380800000, "o": 100, "h": 101, "l": 99, "c": 100.5, "v": 1234, "adjusted": True},
        ]
        writer = Mock()
        writer.write.return_value = type("Result", (), {"written_count": 1, "status": type("Status", (), {"value": "success"})()})()
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db", "POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch.object(mod, "_build_polygon_client", return_value=fake_client), patch.object(
            mod, "OhlcvWriter", return_value=writer
        ), patch("builtins.print") as print_mock, patch("sys.argv", self._argv("--confirm-write")):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("status=partial_fill", printed)
        self.assertIn("remaining_missing_dates_count=1", printed)
        self.assertIn("rows_filtered_out=", printed)
        self.assertEqual(connection.execute.call_count, 2)

    def test_completed_status_when_post_write_coverage_has_no_gaps(self) -> None:
        mod = self._module()
        connection = Mock()
        first = Mock()
        first.fetchall.return_value = [
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 2, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 3, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 6, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 7, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 8, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
        ]
        second = Mock()
        second.fetchall.return_value = [
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 2, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 3, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 6, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 7, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 8, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 9, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 10, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
        ]
        connection.execute.side_effect = [first, second]
        fake_client = Mock()
        fake_client.fetch_aggregates_raw.return_value = [
            {"ticker": "SPY", "t": 1736380800000, "o": 100, "h": 101, "l": 99, "c": 100.5, "v": 1234, "adjusted": True},
            {"ticker": "SPY", "t": 1736467200000, "o": 101, "h": 102, "l": 100, "c": 101.5, "v": 1234, "adjusted": True},
        ]
        writer = Mock()
        writer.write.return_value = type("Result", (), {"written_count": 2, "status": type("Status", (), {"value": "success"})()})()
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db", "POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch.object(mod, "_build_polygon_client", return_value=fake_client), patch.object(
            mod, "OhlcvWriter", return_value=writer
        ), patch("builtins.print") as print_mock, patch("sys.argv", self._argv("--confirm-write")):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("status=completed", printed)
        self.assertIn("remaining_missing_dates_count=0", printed)

    def test_post_write_coverage_recheck_is_read_only(self) -> None:
        mod = self._module()
        connection = Mock()
        first = Mock()
        first.fetchall.return_value = [
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 2, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
        ]
        second = Mock()
        second.fetchall.return_value = first.fetchall.return_value
        connection.execute.side_effect = [first, second]
        fake_client = Mock()
        fake_client.fetch_aggregates_raw.return_value = [
            {"ticker": "SPY", "t": 1736121600000, "o": 100, "h": 101, "l": 99, "c": 100.5, "v": 1234, "adjusted": True},
        ]
        writer = Mock()
        writer.write.return_value = type("Result", (), {"written_count": 1, "status": type("Status", (), {"value": "success"})()})()
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db", "POLYGON_API_KEY": "polygon-secret"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch.object(mod, "_build_polygon_client", return_value=fake_client), patch.object(
            mod, "OhlcvWriter", return_value=writer
        ), patch("builtins.print"), patch("sys.argv", self._argv("--confirm-write")):
            mod.main()

        connection.commit.assert_not_called()
        connection.rollback.assert_not_called()

    def test_no_checkpoint_update(self) -> None:
        mod = self._module()
        self.assertFalse(hasattr(mod, "checkpoint_store"))

    def test_safe_output_no_secrets(self) -> None:
        mod = self._module()
        connection = Mock()
        result = Mock()
        result.fetchall.return_value = [
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 2, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
            {"symbol": "SPY", "timestamp": datetime(2025, 1, 3, tzinfo=timezone.utc), "source": "polygon_aggregates", "adjusted": True},
        ]
        connection.execute.return_value = result
        fake_client = Mock()
        fake_client.fetch_aggregates_raw.return_value = []
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://example/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch.object(mod, "_build_polygon_client", return_value=fake_client), patch(
            "builtins.print"
        ) as print_mock, patch("sys.argv", self._argv()):
            with self.assertRaises(RuntimeError):
                mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertNotIn("DATABASE_URL", printed)
        self.assertNotIn("POLYGON_API_KEY", printed)
