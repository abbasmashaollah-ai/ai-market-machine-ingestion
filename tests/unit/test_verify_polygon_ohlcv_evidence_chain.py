from __future__ import annotations

import os
import unittest
from datetime import date, datetime, timezone
from unittest.mock import patch


class _Result:
    def __init__(self, rows: list[dict[str, object]] | None = None) -> None:
        self._rows = rows or []

    def fetchall(self) -> list[dict[str, object]]:
        return self._rows


class _Connection:
    def __init__(self, rows_by_query: list[tuple[str, list[dict[str, object]]]]) -> None:
        self.rows_by_query = rows_by_query
        self.executed: list[tuple[str, tuple[object, ...]]] = []
        self.closed = False

    def execute(self, sql: str, params: tuple[object, ...] = ()):
        self.executed.append((sql, params))
        for needle, rows in self.rows_by_query:
            if needle in sql:
                return _Result(rows)
        return _Result([])

    def close(self) -> None:
        self.closed = True


class VerifyPolygonOhlcvEvidenceChainTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.verify_polygon_ohlcv_evidence_chain as mod

        return mod

    def _complete_connection(self) -> _Connection:
        return _Connection(
            [
                (
                    "FROM canonical_ohlcv",
                    [
                        {"symbol": "SPY", "timestamp": datetime(2025, 1, 2, tzinfo=timezone.utc), "source": "polygon", "adjusted": True},
                        {"symbol": "SPY", "timestamp": datetime(2025, 1, 3, tzinfo=timezone.utc), "source": "polygon", "adjusted": True},
                    ],
                ),
                ("FROM ingestion_runs", [{"status": "success", "run_id": "run-1", "job_id": "job-1"}]),
                ("FROM data_quality_results", [{"status": "pass", "severity": "info"}]),
                ("FROM data_lineage", [{"quality_status": "pass"}]),
            ]
        )

    def test_complete_evidence_chain(self) -> None:
        mod = self._module()
        connection = self._complete_connection()
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "verify_polygon_ohlcv_evidence_chain.py",
                "--symbol",
                "SPY",
                "--start-date",
                "2025-01-02",
                "--end-date",
                "2025-01-03",
                "--timeframe",
                "1d",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("evidence_status=complete", printed)
        self.assertIn("coverage_ratio=1.000", printed)
        self.assertIn("latest_run_status=success", printed)
        self.assertIn("latest_quality_status=pass", printed)
        self.assertIn("latest_lineage_quality_status=pass", printed)
        self.assertTrue(connection.closed)

    def test_missing_canonical_rows(self) -> None:
        mod = self._module()
        connection = _Connection(
            [
                ("FROM canonical_ohlcv", []),
                ("FROM ingestion_runs", [{"status": "success"}]),
                ("FROM data_quality_results", [{"status": "pass"}]),
                ("FROM data_lineage", [{"quality_status": "pass"}]),
            ]
        )
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["verify_polygon_ohlcv_evidence_chain.py", "--symbol", "SPY", "--start-date", "2025-01-02", "--end-date", "2025-01-03"],
        ):
            mod.main()

        self.assertIn("evidence_status=missing", "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls))

    def test_missing_quality_or_lineage(self) -> None:
        mod = self._module()
        connection = _Connection(
            [
                (
                    "FROM canonical_ohlcv",
                    [{"symbol": "SPY", "timestamp": datetime(2025, 1, 2, tzinfo=timezone.utc), "source": "polygon", "adjusted": True}],
                ),
                ("FROM ingestion_runs", [{"status": "success"}]),
                ("FROM data_quality_results", []),
                ("FROM data_lineage", []),
            ]
        )
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["verify_polygon_ohlcv_evidence_chain.py", "--symbol", "SPY", "--start-date", "2025-01-02", "--end-date", "2025-01-03"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("evidence_status=missing", printed)
        self.assertIn("quality_results_count=0", printed)
        self.assertIn("lineage_rows_count=0", printed)

    def test_no_polygon_key_required_and_database_required(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch.object(mod, "load_local_env_if_available", return_value=False), patch(
            "sys.argv",
            ["verify_polygon_ohlcv_evidence_chain.py", "--symbol", "SPY", "--start-date", "2025-01-02", "--end-date", "2025-01-03"],
        ):
            with self.assertRaises(RuntimeError):
                mod.main()

    def test_no_db_writes_or_vendor_calls(self) -> None:
        mod = self._module()
        connection = self._complete_connection()
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch("builtins.print"), patch(
            "sys.argv",
            ["verify_polygon_ohlcv_evidence_chain.py", "--symbol", "SPY", "--start-date", "2025-01-02", "--end-date", "2025-01-03"],
        ):
            mod.main()

        self.assertFalse(any("INSERT INTO" in sql.upper() for sql, _ in connection.executed))
        self.assertFalse(any("POLYGON" in sql.upper() for sql, _ in connection.executed if "SELECT" in sql.upper()))

