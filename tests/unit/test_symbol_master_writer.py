from __future__ import annotations

import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.normalization.symbol_master import NormalizedSymbolMasterRecord
from app.writers.canonical_writer import WriteStatus
from app.writers.symbol_master_writer import SymbolMasterWriter


class SymbolMasterWriterTests(unittest.TestCase):
    @staticmethod
    def _connection() -> Mock:
        connection = Mock()
        result = Mock()
        result.fetchall.return_value = [
            {"column_name": "symbol"},
            {"column_name": "vendor"},
            {"column_name": "vendor_symbol"},
            {"column_name": "exchange"},
            {"column_name": "asset_type"},
            {"column_name": "name"},
            {"column_name": "currency"},
            {"column_name": "active"},
            {"column_name": "first_seen_at"},
            {"column_name": "last_seen_at"},
            {"column_name": "created_at"},
            {"column_name": "updated_at"},
        ]
        connection.execute.side_effect = [
            result,
            SimpleNamespace(fetchall=lambda: [{"indexdef": "CREATE UNIQUE INDEX uq_symbol_master_symbol ON public.symbol_master USING btree (symbol)"}]),
            SimpleNamespace(rowcount=1),
            SimpleNamespace(rowcount=1),
        ]
        return connection

    def test_accepts_normalized_symbol_record_objects(self) -> None:
        connection = self._connection()
        writer = SymbolMasterWriter(connection)
        records = [
            NormalizedSymbolMasterRecord(
                symbol="AAPL",
                active=True,
                vendor="fmp",
                vendor_symbol="AAPL",
                asset_type="equity",
                exchange="NASDAQ",
                name="Apple Inc.",
                currency="USD",
                first_seen_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
                last_seen_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
            )
        ]

        result = writer.write(records)

        self.assertEqual(result.status, WriteStatus.SUCCESS)
        self.assertEqual(result.written_count, 1)
        self.assertTrue(connection.commit.called)

    def test_deduplication(self) -> None:
        connection = self._connection()
        writer = SymbolMasterWriter(connection)
        records = [
            NormalizedSymbolMasterRecord(symbol="AAPL", active=True, vendor="fmp", vendor_symbol="AAPL"),
            NormalizedSymbolMasterRecord(symbol="AAPL", active=True, vendor="fmp", vendor_symbol="AAPL"),
        ]

        result = writer.write(records)

        self.assertEqual(result.skipped_count, 1)
        self.assertEqual(result.written_count, 1)

    def test_rollback_on_failure(self) -> None:
        connection = self._connection()
        connection.execute.side_effect = RuntimeError("boom")
        writer = SymbolMasterWriter(connection)
        result = writer.write([NormalizedSymbolMasterRecord(symbol="AAPL", active=True, vendor="fmp", vendor_symbol="AAPL")])

        self.assertEqual(result.status, WriteStatus.FAILURE)
        self.assertTrue(connection.rollback.called)

    def test_source_has_no_forbidden_imports(self) -> None:
        source = __import__("pathlib").Path("app/writers/symbol_master_writer.py").read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", source)
        self.assertNotIn("APIRouter", source)
        self.assertNotIn("alembic", source.lower())
        self.assertNotIn("ai_market_machine_data", source)
        self.assertNotIn("requests", source.lower())
        self.assertNotIn("httpx", source.lower())
