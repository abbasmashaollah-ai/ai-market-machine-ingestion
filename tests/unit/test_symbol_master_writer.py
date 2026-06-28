from __future__ import annotations

import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.normalization.symbol_master import (
    NormalizedSymbolMasterRecord,
    SymbolMasterSourceRecord,
    build_symbol_identity_idempotency_key,
    normalize_symbol_record,
    validate_source_record,
)
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
                source_vendor="fmp",
                source_dataset="symbol_master",
                source_sha256="sha-aapl",
                source_file_name="aapl.json",
                source_file_path="fixtures/symbol_master/aapl.json",
                producer_run_id="run-001",
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
        self.assertIn("idempotency_keys", result.details)
        self.assertEqual(
            result.details["idempotency_keys"],
            (build_symbol_identity_idempotency_key("fmp", "symbol_master", "sha-aapl", "equity", "AAPL"),),
        )

    def test_deduplication(self) -> None:
        connection = self._connection()
        writer = SymbolMasterWriter(connection)
        records = [
            NormalizedSymbolMasterRecord(symbol="AAPL", active=True, vendor="fmp", source_vendor="fmp", source_dataset="symbol_master", source_sha256="sha-aapl", vendor_symbol="AAPL", asset_type="equity"),
            NormalizedSymbolMasterRecord(symbol="AAPL", active=True, vendor="fmp", source_vendor="fmp", source_dataset="symbol_master", source_sha256="sha-aapl", vendor_symbol="AAPL", asset_type="equity"),
        ]

        result = writer.write(records)

        self.assertEqual(result.skipped_count, 1)
        self.assertEqual(result.written_count, 1)

    def test_rollback_on_failure(self) -> None:
        connection = self._connection()
        connection.execute.side_effect = RuntimeError("boom")
        writer = SymbolMasterWriter(connection)
        result = writer.write([NormalizedSymbolMasterRecord(symbol="AAPL", active=True, vendor="fmp", source_vendor="fmp", source_dataset="symbol_master", source_sha256="sha-aapl", vendor_symbol="AAPL", asset_type="equity")])

        self.assertEqual(result.status, WriteStatus.FAILURE)
        self.assertTrue(connection.rollback.called)

    def test_idempotency_key_helper_is_deterministic(self) -> None:
        key = build_symbol_identity_idempotency_key("fmp", "symbol_master", "sha-aapl", "equity", "AAPL")
        self.assertEqual(key, build_symbol_identity_idempotency_key("fmp", "symbol_master", "sha-aapl", "equity", "AAPL"))
        self.assertNotEqual(key, build_symbol_identity_idempotency_key("fmp", "symbol_master", "sha-msft", "equity", "AAPL"))
        self.assertNotEqual(key, build_symbol_identity_idempotency_key("fmp", "symbol_master", "sha-aapl", "etf", "AAPL"))
        self.assertNotEqual(key, build_symbol_identity_idempotency_key("fmp", "symbol_master", "sha-aapl", "equity", "MSFT"))

    def test_normalization_preserves_evidence_fields(self) -> None:
        source = SymbolMasterSourceRecord(
            symbol=" AAPL ",
            active=True,
            vendor=" fmp ",
            source_vendor=" fmp ",
            source_dataset=" symbol_master ",
            source_sha256=" sha-aapl ",
            source_file_name=" aapl.json ",
            source_file_path=" fixtures/symbol_master/aapl.json ",
            producer_run_id=" run-001 ",
            vendor_symbol=" AAPL ",
            asset_type=" equity ",
        )
        normalized = normalize_symbol_record(source)
        self.assertEqual(normalized.symbol, "AAPL")
        self.assertEqual(normalized.vendor, "fmp")
        self.assertEqual(normalized.source_vendor, "fmp")
        self.assertEqual(normalized.source_dataset, "symbol_master")
        self.assertEqual(normalized.source_sha256, "sha-aapl")
        self.assertEqual(normalized.source_file_name, "aapl.json")
        self.assertEqual(normalized.source_file_path, "fixtures/symbol_master/aapl.json")
        self.assertEqual(normalized.producer_run_id, "run-001")

    def test_validate_source_record_checks_evidence_fields(self) -> None:
        source = SymbolMasterSourceRecord(
            symbol="AAPL",
            active=True,
            vendor="fmp",
            source_vendor=" ",
        )
        errors = validate_source_record(source)
        self.assertIn("source_vendor cannot be empty", errors)

    def test_source_has_no_forbidden_imports(self) -> None:
        source = __import__("pathlib").Path("app/writers/symbol_master_writer.py").read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", source)
        self.assertNotIn("APIRouter", source)
        self.assertNotIn("alembic", source.lower())
        self.assertNotIn("ai_market_machine_data", source)
        self.assertNotIn("requests", source.lower())
        self.assertNotIn("httpx", source.lower())
