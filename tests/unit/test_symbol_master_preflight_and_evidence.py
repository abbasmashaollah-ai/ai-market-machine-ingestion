from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


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


class SymbolMasterPreflightAndEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _preflight_module(self):
        import scripts.preflight_symbol_master_operations as mod

        return mod

    def _evidence_module(self):
        import scripts.verify_symbol_master_evidence_chain as mod

        return mod

    def _complete_connection(self) -> _Connection:
        return _Connection(
            [
                ("COUNT(*) AS row_count", [{"row_count": 2, "active_count": 1, "inactive_count": 1}]),
                ("WHERE symbol = %s", [{"symbol": "AAPL"}]),
            ]
        )

    def test_preflight_success(self) -> None:
        mod = self._preflight_module()
        with patch.dict(os.environ, {}, clear=True), patch(
            "scripts.preflight_symbol_master_operations.load_local_env_if_available", return_value=False
        ), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["preflight_symbol_master_operations.py"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("symbol_master_preflight_status=PASS", printed)
        self.assertIn("inventory_ok=True", printed)
        self.assertIn("writer_doc_exists=True", printed)
        self.assertIn("foundation_doc_exists=True", printed)
        self.assertIn("polygon_doc_exists=True", printed)

    def test_preflight_database_url_required_only_for_confirm_or_check_existing(self) -> None:
        mod = self._preflight_module()
        with patch.dict(os.environ, {}, clear=True), patch(
            "scripts.preflight_symbol_master_operations.load_local_env_if_available", return_value=False
        ), patch("sys.argv", ["preflight_symbol_master_operations.py", "--confirm-write"]):
            with self.assertRaises(RuntimeError):
                mod.main()

    def test_preflight_check_existing_requires_database_url(self) -> None:
        mod = self._preflight_module()
        with patch.dict(os.environ, {}, clear=True), patch(
            "scripts.preflight_symbol_master_operations.load_local_env_if_available", return_value=False
        ), patch("sys.argv", ["preflight_symbol_master_operations.py", "--check-existing"]):
            with self.assertRaises(RuntimeError):
                mod.main()

    def test_preflight_source_has_no_forbidden_imports(self) -> None:
        text = Path("scripts/preflight_symbol_master_operations.py").read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("import requests", text.lower())
        self.assertNotIn("import httpx", text.lower())
        self.assertNotIn("from ai_market_machine_data", text.lower())
        self.assertNotIn("import alembic", text.lower())

    def test_polygon_command_inventory_is_present(self) -> None:
        import scripts.verify_manual_ingestion_commands as inventory

        self.assertIn("scripts.dry_run_polygon_symbol_master", inventory.MODULES)

    def test_polygon_preflight_docs_cover_command(self) -> None:
        text = Path("docs/symbol_master_preflight.md").read_text(encoding="utf-8").lower()
        self.assertIn("polygon symbol master runner", text)
        self.assertIn("polygon_api_key", text)

    def test_preflight_no_db_access_or_vendor_calls_without_flags(self) -> None:
        mod = self._preflight_module()
        with patch.dict(os.environ, {}, clear=True), patch(
            "scripts.preflight_symbol_master_operations.load_local_env_if_available", return_value=False
        ), patch.object(mod, "_require_database_url", wraps=mod._require_database_url), patch.object(
            mod, "_check_inventory", wraps=mod._check_inventory
        ), patch.object(mod, "_assert_text_not_present", wraps=mod._assert_text_not_present), patch(
            "sys.argv",
            ["preflight_symbol_master_operations.py"],
        ):
            mod.main()

    def test_evidence_verifier_counts_and_symbol_found(self) -> None:
        mod = self._evidence_module()
        connection = self._complete_connection()
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["verify_symbol_master_evidence_chain.py", "--symbol", "AAPL"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("row_count=2", printed)
        self.assertIn("active_count=1", printed)
        self.assertIn("inactive_count=1", printed)
        self.assertIn("symbol_found=True", printed)
        self.assertIn("evidence_status=PASS", printed)
        self.assertTrue(connection.closed)

    def test_evidence_verifier_warns_when_empty_without_symbol(self) -> None:
        mod = self._evidence_module()
        connection = _Connection([("COUNT(*) AS row_count", [{"row_count": 0, "active_count": 0, "inactive_count": 0}])])
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["verify_symbol_master_evidence_chain.py"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("row_count=0", printed)
        self.assertIn("evidence_status=WARN", printed)

    def test_evidence_verifier_fail_on_missing_symbol(self) -> None:
        mod = self._evidence_module()
        connection = _Connection([("COUNT(*) AS row_count", [{"row_count": 1, "active_count": 1, "inactive_count": 0}])])
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["verify_symbol_master_evidence_chain.py", "--symbol", "MSFT"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("symbol_found=False", printed)
        self.assertIn("symbol_status=FAIL", printed)
        self.assertIn("evidence_status=FAIL", printed)

    def test_evidence_verifier_source_has_no_forbidden_imports(self) -> None:
        text = Path("scripts/verify_symbol_master_evidence_chain.py").read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("import requests", text.lower())
        self.assertNotIn("import httpx", text.lower())
        self.assertNotIn("ai_market_machine_data", text)
        self.assertNotIn("alembic", text.lower())

    def test_evidence_verifier_no_db_writes_or_vendor_calls(self) -> None:
        mod = self._evidence_module()
        connection = self._complete_connection()
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch("builtins.print"), patch(
            "sys.argv",
            ["verify_symbol_master_evidence_chain.py", "--symbol", "AAPL"],
        ):
            mod.main()

        self.assertFalse(any("INSERT INTO" in sql.upper() for sql, _ in connection.executed))
        self.assertTrue(any("SELECT" in sql.upper() for sql, _ in connection.executed))
