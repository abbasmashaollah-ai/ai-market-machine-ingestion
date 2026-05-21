from __future__ import annotations

import sqlite3
import unittest
from datetime import datetime, timezone

from app.models.normalized import NormalizedMacroObservation
from app.writers.canonical_writer import WriteStatus
from app.writers.macro_writer import MacroWriter, build_macro_writer


class MacroWriterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute(
            """
            CREATE TABLE macro_rate_observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                series_id TEXT NOT NULL,
                observation_date TEXT NOT NULL,
                value REAL NULL,
                source TEXT NOT NULL,
                release_timestamp TEXT NULL,
                revision_timestamp TEXT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(series_id, observation_date, source)
            )
            """
        )

    def tearDown(self) -> None:
        self.conn.close()

    def _record(self, *, value: object = 1.23, source: str | None = None) -> NormalizedMacroObservation:
        return NormalizedMacroObservation(
            symbol="GDP",
            symbol_id="GDP",
            timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
            value=value,  # type: ignore[arg-type]
            vendor="FRED",
            source=source,
        )

    def test_writes_row_without_suppling_id(self) -> None:
        writer = MacroWriter(self.conn)
        result = writer.write([self._record()])

        self.assertEqual(result.status, WriteStatus.SUCCESS)
        row = self.conn.execute("SELECT id, series_id, observation_date, value, source, created_at FROM macro_rate_observations").fetchone()
        self.assertEqual(row[1], "GDP")
        self.assertEqual(row[2], "2026-01-01")
        self.assertEqual(row[3], 1.23)
        self.assertEqual(row[4], "FRED")
        self.assertEqual(result.written_count, 1)

    def test_missing_fred_value_becomes_null(self) -> None:
        writer = MacroWriter(self.conn)
        result = writer.write([self._record(value=".")])

        self.assertEqual(result.status, WriteStatus.SUCCESS)
        value = self.conn.execute("SELECT value FROM macro_rate_observations").fetchone()[0]
        self.assertIsNone(value)

    def test_duplicate_natural_key_is_collapsed_within_batch(self) -> None:
        writer = MacroWriter(self.conn)
        records = [self._record(), self._record(value=4.56)]

        result = writer.write(records)

        self.assertEqual(result.status, WriteStatus.SUCCESS)
        count = self.conn.execute("SELECT COUNT(*) FROM macro_rate_observations").fetchone()[0]
        self.assertEqual(count, 1)
        self.assertEqual(result.skipped_count, 1)

    def test_duplicate_natural_key_upserts_existing_row(self) -> None:
        self.conn.execute(
            """
            INSERT INTO macro_rate_observations (
                series_id, observation_date, value, source, release_timestamp, revision_timestamp, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            ("GDP", "2026-01-01", 1.0, "FRED", None, None, "2026-01-01T00:00:00+00:00"),
        )
        writer = MacroWriter(self.conn)

        result = writer.write([self._record(value=2.5)])

        self.assertEqual(result.status, WriteStatus.SUCCESS)
        value = self.conn.execute("SELECT value FROM macro_rate_observations WHERE series_id = 'GDP'").fetchone()[0]
        self.assertEqual(value, 2.5)

    def test_no_rows_skips_cleanly(self) -> None:
        writer = MacroWriter(self.conn)
        result = writer.write([])

        self.assertEqual(result.status, WriteStatus.SKIPPED)
        self.assertEqual(result.written_count, 0)

    def test_build_macro_writer_wraps_connection(self) -> None:
        writer = build_macro_writer(self.conn)
        self.assertIsInstance(writer, MacroWriter)
