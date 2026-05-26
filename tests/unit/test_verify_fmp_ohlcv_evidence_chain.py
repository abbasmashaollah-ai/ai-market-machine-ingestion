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


class VerifyFmpOhlcvEvidenceChainTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.verify_fmp_ohlcv_evidence_chain as mod

        return mod

    def _connection(
        self,
        *,
        canonical_rows: list[dict[str, object]] | None = None,
        run_rows: list[dict[str, object]] | None = None,
        quality_rows: list[dict[str, object]] | None = None,
        lineage_rows: list[dict[str, object]] | None = None,
    ) -> _Connection:
        return _Connection(
            [
                ("FROM canonical_ohlcv", canonical_rows or []),
                ("FROM ingestion_runs", run_rows or []),
                ("FROM data_quality_results", quality_rows or []),
                ("FROM data_lineage", lineage_rows or []),
            ]
        )

    def test_confirmed_write_evidence_chain_passes(self) -> None:
        mod = self._module()
        connection = self._connection(
            canonical_rows=[
                {"symbol": "AAPL", "timestamp": datetime(2026, 1, 2, tzinfo=timezone.utc), "source": "fmp", "adjusted": True},
                {"symbol": "AAPL", "timestamp": datetime(2026, 1, 3, tzinfo=timezone.utc), "source": "fmp", "adjusted": True},
            ],
            run_rows=[{"status": "success", "run_id": "run-1"}],
            quality_rows=[{"status": "pass", "severity": "info"}],
            lineage_rows=[{"quality_status": "pass"}],
        )
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "verify_fmp_ohlcv_evidence_chain.py",
                "--symbol",
                "AAPL",
                "--start-date",
                "2026-01-02",
                "--end-date",
                "2026-01-03",
                "--timeframe",
                "1d",
                "--confirmed-write",
                "--record-run",
                "--record-quality",
                "--record-lineage",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("canonical_status=PASS", printed)
        self.assertIn("run_status=PASS", printed)
        self.assertIn("quality_status=PASS", printed)
        self.assertIn("lineage_status=PASS", printed)
        self.assertIn("evidence_status=PASS", printed)
        self.assertTrue(connection.closed)

    def test_dry_run_without_canonical_rows_passes(self) -> None:
        mod = self._module()
        connection = self._connection()
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "verify_fmp_ohlcv_evidence_chain.py",
                "--symbol",
                "AAPL",
                "--start-date",
                "2026-01-02",
                "--end-date",
                "2026-01-03",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("canonical_status=PASS", printed)
        self.assertIn("run_status=PASS", printed)
        self.assertIn("quality_status=PASS", printed)
        self.assertIn("lineage_status=PASS", printed)
        self.assertIn("evidence_status=PASS", printed)

    def test_record_quality_without_rows_fails(self) -> None:
        mod = self._module()
        connection = self._connection(
            canonical_rows=[
                {"symbol": "AAPL", "timestamp": datetime(2026, 1, 2, tzinfo=timezone.utc), "source": "fmp", "adjusted": True},
            ]
        )
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "verify_fmp_ohlcv_evidence_chain.py",
                "--symbol",
                "AAPL",
                "--start-date",
                "2026-01-02",
                "--end-date",
                "2026-01-03",
                "--record-quality",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("quality_status=FAIL", printed)
        self.assertIn("evidence_status=FAIL", printed)

    def test_record_lineage_without_rows_fails(self) -> None:
        mod = self._module()
        connection = self._connection(
            canonical_rows=[
                {"symbol": "AAPL", "timestamp": datetime(2026, 1, 2, tzinfo=timezone.utc), "source": "fmp", "adjusted": True},
            ]
        )
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "verify_fmp_ohlcv_evidence_chain.py",
                "--symbol",
                "AAPL",
                "--start-date",
                "2026-01-02",
                "--end-date",
                "2026-01-03",
                "--record-lineage",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("lineage_status=FAIL", printed)
        self.assertIn("evidence_status=FAIL", printed)

    def test_confirmed_write_without_canonical_rows_fails(self) -> None:
        mod = self._module()
        connection = self._connection()
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            [
                "verify_fmp_ohlcv_evidence_chain.py",
                "--symbol",
                "AAPL",
                "--start-date",
                "2026-01-02",
                "--end-date",
                "2026-01-03",
                "--confirmed-write",
            ],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("canonical_status=FAIL", printed)
        self.assertIn("evidence_status=FAIL", printed)

    def test_source_has_no_api_scheduler_or_migration_imports(self) -> None:
        source = __import__("pathlib").Path("scripts/verify_fmp_ohlcv_evidence_chain.py").read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", source)
        self.assertNotIn("APIRouter", source)
        self.assertNotIn("scheduler", source.lower())
        self.assertNotIn("migration", source.lower())
        self.assertNotIn("schema", source.lower())

