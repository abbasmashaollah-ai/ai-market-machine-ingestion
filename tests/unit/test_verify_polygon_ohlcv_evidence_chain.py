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
                ("FROM ingestion_checkpoints", [{"checkpoint_id": "polygon:ohlcv:SPY:1d:2025-01-02:2025-01-03", "status": "completed", "last_successful_date": date(2025, 1, 3)}]),
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
                "--confirmed-write",
                "--record-run",
                "--record-quality",
                "--record-lineage",
                "--resume-from-checkpoint",
                "--chunk-days",
                "10",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("evidence_status=PASS", printed)
        self.assertIn("coverage_ratio=1.000", printed)
        self.assertIn("latest_run_status=success", printed)
        self.assertIn("latest_quality_status=pass", printed)
        self.assertIn("latest_lineage_quality_status=pass", printed)
        self.assertIn("canonical_status=PASS", printed)
        self.assertIn("run_status=PASS", printed)
        self.assertIn("quality_status=PASS", printed)
        self.assertIn("lineage_status=PASS", printed)
        self.assertIn("checkpoint_status=PASS", printed)
        self.assertIn("run_match_mode=exact", printed)
        self.assertIn("quality_match_mode=exact", printed)
        self.assertIn("lineage_match_mode=exact", printed)
        self.assertTrue(connection.closed)

    def test_dry_run_evidence_chain_does_not_require_canonical_writes(self) -> None:
        mod = self._module()
        connection = _Connection(
            [
                ("FROM canonical_ohlcv", []),
                ("FROM ingestion_runs", []),
                ("FROM data_quality_results", []),
                ("FROM data_lineage", []),
                ("FROM ingestion_checkpoints", []),
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
        self.assertIn("evidence_status=PASS", printed)
        self.assertIn("canonical_status=PASS", printed)
        self.assertIn("run_status=PASS", printed)
        self.assertIn("quality_status=PASS", printed)
        self.assertIn("lineage_status=PASS", printed)
        self.assertIn("checkpoint_status=PASS", printed)

    def test_missing_quality_or_lineage_without_flags_is_pass(self) -> None:
        mod = self._module()
        connection = _Connection(
            [
                (
                    "FROM canonical_ohlcv",
                    [
                        {"symbol": "SPY", "timestamp": datetime(2025, 1, 2, tzinfo=timezone.utc), "source": "polygon", "adjusted": True},
                        {"symbol": "SPY", "timestamp": datetime(2025, 1, 3, tzinfo=timezone.utc), "source": "polygon", "adjusted": True},
                    ],
                ),
                ("FROM ingestion_runs", []),
                ("FROM data_quality_results", []),
                ("FROM data_lineage", []),
                ("FROM ingestion_checkpoints", []),
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
        self.assertIn("canonical_status=WARN", printed)
        self.assertIn("quality_status=PASS", printed)
        self.assertIn("lineage_status=PASS", printed)
        self.assertIn("evidence_status=WARN", printed)

    def test_missing_quality_or_lineage_with_flags_fails(self) -> None:
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
                ("FROM ingestion_checkpoints", []),
            ]
        )
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
                "--record-quality",
                "--record-lineage",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("quality_status=FAIL", printed)
        self.assertIn("lineage_status=FAIL", printed)
        self.assertIn("evidence_status=FAIL", printed)

    def test_missing_canonical_rows_for_confirmed_write_fails(self) -> None:
        mod = self._module()
        connection = _Connection(
            [
                ("FROM canonical_ohlcv", []),
                ("FROM ingestion_runs", [{"status": "success"}]),
                ("FROM data_quality_results", []),
                ("FROM data_lineage", []),
                ("FROM ingestion_checkpoints", []),
            ]
        )
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
                "--confirmed-write",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("canonical_status=FAIL", printed)
        self.assertIn("evidence_status=FAIL", printed)

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
        self.assertTrue(any("SELECT" in sql.upper() for sql, _ in connection.executed))

    def test_checkpoint_mismatch_fails_when_resuming(self) -> None:
        mod = self._module()
        connection = _Connection(
            [
                (
                    "FROM canonical_ohlcv",
                    [{"symbol": "SPY", "timestamp": datetime(2025, 1, 2, tzinfo=timezone.utc), "source": "polygon", "adjusted": True}],
                ),
                ("FROM ingestion_runs", [{"status": "success"}]),
                ("FROM data_quality_results", [{"status": "pass"}]),
                ("FROM data_lineage", [{"quality_status": "pass"}]),
                ("FROM ingestion_checkpoints", [{"checkpoint_id": "polygon:ohlcv:SPY:1d:2025-01-02:2025-01-03", "status": "completed", "last_successful_date": date(2025, 1, 2)}]),
            ]
        )
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
                "--confirmed-write",
                "--record-run",
                "--record-quality",
                "--record-lineage",
                "--resume-from-checkpoint",
                "--chunk-days",
                "10",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("checkpoint_status=FAIL", printed)
        self.assertIn("checkpoint_failures=1", printed)
        self.assertIn("evidence_status=FAIL", printed)

    def test_source_has_no_api_scheduler_or_migration_imports(self) -> None:
        import pathlib

        source = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "verify_polygon_ohlcv_evidence_chain.py"
        text = source.read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("scheduler", text.lower())
        self.assertNotIn("migration", text.lower())
        self.assertNotIn("schema", text.lower())
