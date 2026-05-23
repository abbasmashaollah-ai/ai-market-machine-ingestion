from __future__ import annotations

import os
import unittest
from unittest.mock import patch


class _Result:
    def __init__(self, rows: list[dict[str, object]] | None = None) -> None:
        self._rows = rows or []

    def fetchall(self) -> list[dict[str, object]]:
        return self._rows


class _Connection:
    def __init__(self) -> None:
        self.executed: list[tuple[str, tuple[object, ...]]] = []
        self.closed = False

    def execute(self, sql: str, params: tuple[object, ...] = ()):
        self.executed.append((sql, params))
        return _Result([])

    def close(self) -> None:
        self.closed = True


class InspectDataLineageTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env)

    def test_is_read_only(self) -> None:
        import scripts.inspect_data_lineage as mod

        connection = _Connection()
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}, clear=True), patch.object(
            mod, "load_local_env_if_available", return_value=False
        ), patch.object(mod, "_open_connection", return_value=connection), patch("builtins.print"), patch(
            "sys.argv",
            ["inspect_data_lineage.py", "--vendor", "polygon", "--dataset", "ohlcv", "--limit", "3"],
        ):
            mod.main()

        self.assertTrue(connection.closed)
        self.assertTrue(connection.executed)
        self.assertTrue(all("SELECT" in sql.upper() for sql, _ in connection.executed))
