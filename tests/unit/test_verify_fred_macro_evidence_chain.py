from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest.mock import patch


class _Result:
    def __init__(self, rows: list[dict[str, object]] | None = None) -> None:
        self._rows = rows or []

    def fetchall(self) -> list[dict[str, object]]:
        return self._rows


class _Connection:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows
        self.executed: list[tuple[str, tuple[object, ...]]] = []
        self.closed = False

    def execute(self, sql: str, params: tuple[object, ...] = ()):
        self.executed.append((sql, params))
        return _Result(self.rows)

    def close(self) -> None:
        self.closed = True


class VerifyFredMacroEvidenceChainTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.verify_fred_macro_evidence_chain as mod

        return mod

    def _rows(self, *, include_missing_value: bool = False) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for series_id in ("DGS10", "DGS2", "FEDFUNDS", "CPIAUCSL", "UNRATE"):
            rows.append({"series_id": series_id, "observation_date": "2026-01-01", "value": None if include_missing_value and series_id == "DGS10" else 1.0, "source": "fred"})
            rows.append({"series_id": series_id, "observation_date": "2026-01-03", "value": 2.0, "source": "fred"})
        return rows

    def test_pass_with_all_starter_series(self) -> None:
        mod = self._module()
        connection = _Connection(self._rows())
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["verify_fred_macro_evidence_chain.py"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("series_count=5", printed)
        self.assertIn("total_rows=10", printed)
        self.assertIn("evidence_status=PASS", printed)
        self.assertTrue(connection.closed)

    def test_warn_with_missing_one_series(self) -> None:
        mod = self._module()
        rows = self._rows()
        rows = [row for row in rows if row["series_id"] != "UNRATE"]
        connection = _Connection(rows)
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["verify_fred_macro_evidence_chain.py"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("missing_series=['UNRATE']", printed)
        self.assertIn("evidence_status=WARN", printed)

    def test_fail_with_no_rows(self) -> None:
        mod = self._module()
        connection = _Connection([])
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["verify_fred_macro_evidence_chain.py"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("total_rows=0", printed)
        self.assertIn("evidence_status=FAIL", printed)

    def test_latest_date_max_behavior(self) -> None:
        mod = self._module()
        connection = _Connection(
            [
                {"series_id": "DGS10", "observation_date": "2026-01-01", "value": 1.0, "source": "fred"},
                {"series_id": "DGS10", "observation_date": "2026-01-03", "value": 2.0, "source": "fred"},
                {"series_id": "DGS10", "observation_date": "2026-01-02", "value": 3.0, "source": "fred"},
            ]
        )
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["verify_fred_macro_evidence_chain.py", "--series", "DGS10"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("latest_observation_dates={'DGS10': '2026-01-03'}", printed)

    def test_missing_value_count(self) -> None:
        mod = self._module()
        connection = _Connection(self._rows(include_missing_value=True))
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["verify_fred_macro_evidence_chain.py"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("missing_value_count=1", printed)

    def test_no_vendor_calls_and_no_db_writes(self) -> None:
        mod = self._module()
        connection = _Connection(self._rows())
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch("builtins.print"), patch(
            "sys.argv",
            ["verify_fred_macro_evidence_chain.py"],
        ):
            mod.main()

        self.assertTrue(any("SELECT" in sql.upper() for sql, _ in connection.executed))
        self.assertFalse(any("INSERT" in sql.upper() for sql, _ in connection.executed))

    def test_no_forbidden_imports(self) -> None:
        text = Path("scripts/verify_fred_macro_evidence_chain.py").read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("alembic", text.lower())
        self.assertNotIn("requests", text.lower())
        self.assertNotIn("httpx", text.lower())
        self.assertNotIn("ai_market_machine_data", text)

