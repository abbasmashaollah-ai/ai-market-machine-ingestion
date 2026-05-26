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


class EtfIndexUniverseExpansionTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def _module(self):
        import scripts.dry_run_etf_index_universe_expansion as mod

        return mod

    def test_candidate_generation_and_groups(self) -> None:
        from app.normalization.etf_index_universe import build_etf_index_universe_candidates, summarize_candidate_groups

        candidates = build_etf_index_universe_candidates()
        self.assertGreaterEqual(len(candidates), 20)
        groups = summarize_candidate_groups(candidates)
        self.assertIn("core_etf", groups)
        self.assertIn("sector_etf", groups)
        self.assertIn("major_index", groups)
        self.assertIn("industry_etf_placeholder", groups)

    def test_default_no_db_access(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock, patch("sys.argv", ["dry_run_etf_index_universe_expansion.py"]):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("candidate_count=", printed)
        self.assertIn("found_count=0", printed)
        self.assertIn("missing_count=", printed)
        self.assertIn("no_vendor_calls=True", printed)
        self.assertIn("no_db_writes=True", printed)
        self.assertNotIn("found_symbols=", printed)
        self.assertNotIn("missing_symbols=", printed)

    def test_check_symbol_master_requires_database_url(self) -> None:
        mod = self._module()
        with patch.dict(os.environ, {}, clear=True), patch(
            "scripts.dry_run_etf_index_universe_expansion.load_local_env_if_available", return_value=False
        ), patch("sys.argv", ["dry_run_etf_index_universe_expansion.py", "--check-symbol-master"]):
            with self.assertRaises(RuntimeError):
                mod.main()

    def test_symbol_master_check_found_and_missing_behavior(self) -> None:
        mod = self._module()
        connection = _Connection([{"symbol": "SPY"}, {"symbol": "QQQ"}])
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["dry_run_etf_index_universe_expansion.py", "--check-symbol-master"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("found_count=2", printed)
        self.assertIn("missing_count=", printed)
        self.assertTrue(connection.closed)

    def test_show_missing_output(self) -> None:
        mod = self._module()
        connection = _Connection([{"symbol": "SPY"}])
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["dry_run_etf_index_universe_expansion.py", "--check-symbol-master", "--show-missing"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("missing_symbols=", printed)

    def test_show_found_output(self) -> None:
        mod = self._module()
        connection = _Connection([{"symbol": "SPY"}, {"symbol": "QQQ"}])
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch("builtins.print") as print_mock, patch(
            "sys.argv",
            ["dry_run_etf_index_universe_expansion.py", "--check-symbol-master", "--show-found"],
        ):
            mod.main()

        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("found_symbols=", printed)

    def test_no_vendor_calls_and_no_db_writes(self) -> None:
        mod = self._module()
        with patch("builtins.print"), patch("importlib.import_module") as import_mock, patch(
            "sys.argv", ["dry_run_etf_index_universe_expansion.py"]
        ):
            mod.main([])

        imported_names = [call.args[0] for call in import_mock.mock_calls if call.args]
        self.assertFalse(any(name.startswith("app.vendors") for name in imported_names))
        self.assertFalse(any(name.startswith("app.state") for name in imported_names))

    def test_no_forbidden_imports(self) -> None:
        text = Path("scripts/dry_run_etf_index_universe_expansion.py").read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("alembic", text.lower())
        self.assertNotIn("ai_market_machine_data", text)
        self.assertNotIn("requests", text.lower())
        self.assertNotIn("httpx", text.lower())

    def test_docs_cover_foundation(self) -> None:
        text = Path("docs/etf_index_universe_expansion_foundation.md").read_text(encoding="utf-8").lower()
        self.assertIn("etf/index universe expansion foundation", text)
        self.assertIn("no_vendor_calls=true", text)
        self.assertIn("no_db_writes=true", text)
        self.assertIn("public.symbol_master", text)
        self.assertIn("show-missing", text)
        self.assertIn("show-found", text)

    def test_inventory_contains_command(self) -> None:
        import scripts.verify_manual_ingestion_commands as inventory

        self.assertIn("scripts.dry_run_etf_index_universe_expansion", inventory.MODULES)
