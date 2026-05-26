from __future__ import annotations

import unittest
from datetime import date

from app.normalization.fred_macro import NormalizedFredMacroRecord
from app.writers.fred_macro_writer import FredMacroWriter


class _Result:
    def __init__(self, rowcount: int = 1) -> None:
        self.rowcount = rowcount


class _Connection:
    def __init__(self, *, fail_on_execute: bool = False) -> None:
        self.fail_on_execute = fail_on_execute
        self.executed: list[tuple[str, tuple[object, ...]]] = []
        self.committed = False
        self.rolled_back = False

    def execute(self, sql: str, params: tuple[object, ...] = ()):
        if self.fail_on_execute:
            raise RuntimeError("database unavailable")
        self.executed.append((sql, params))
        return _Result(1)

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


class FredMacroWriterTests(unittest.TestCase):
    def _record(self, value: float | None = 1.0, series_id: str = "DGS10", observation_date: date = date(2026, 1, 1)) -> NormalizedFredMacroRecord:
        return NormalizedFredMacroRecord(
            series_id=series_id,
            observation_date=observation_date,
            value=value,
            source="fred",
            unit="percent",
            frequency="daily",
            notes=None,
        )

    def test_writer_accepts_normalized_records(self) -> None:
        connection = _Connection()
        writer = FredMacroWriter(connection)

        result = writer.write([self._record()])

        self.assertEqual(result.written_count, 1)
        self.assertTrue(connection.committed)
        self.assertFalse(connection.rolled_back)
        self.assertEqual(len(connection.executed), 1)

    def test_dedupe_behavior(self) -> None:
        connection = _Connection()
        writer = FredMacroWriter(connection)

        result = writer.write([self._record(), self._record()])

        self.assertEqual(result.written_count, 1)
        self.assertEqual(result.skipped_count, 1)
        self.assertEqual(len(connection.executed), 1)

    def test_rollback_on_failure(self) -> None:
        connection = _Connection(fail_on_execute=True)
        writer = FredMacroWriter(connection)

        result = writer.write([self._record()])

        self.assertEqual(result.status.value, "failure")
        self.assertTrue(connection.rolled_back)
        self.assertFalse(connection.committed)

    def test_no_vendor_calls_or_forbidden_imports(self) -> None:
        text = __import__("pathlib").Path("app/writers/fred_macro_writer.py").read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("alembic", text.lower())
        self.assertNotIn("requests", text.lower())
        self.assertNotIn("httpx", text.lower())

