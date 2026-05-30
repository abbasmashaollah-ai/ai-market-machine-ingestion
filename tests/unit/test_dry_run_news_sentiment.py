from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch


class NewsSentimentFoundationTests(unittest.TestCase):
    def _module(self):
        import scripts.dry_run_news_sentiment as mod

        return mod

    def test_fixture_generation(self) -> None:
        from app.normalization.news_sentiment import DEFAULT_FIXTURE_RECORDS

        self.assertEqual(len(DEFAULT_FIXTURE_RECORDS), 3)
        tickers = [tuple(record["tickers"]) for record in DEFAULT_FIXTURE_RECORDS]
        self.assertEqual(tickers, [("AAPL",), ("MSFT",), ("NVDA",)])

    def test_normalized_field_alignment(self) -> None:
        from app.normalization.news_sentiment import normalize_news_sentiment_record

        record = normalize_news_sentiment_record(
            {
                "news_id": "news-aapl-2026-05-30-01",
                "published_at": "2026-05-30T14:30:00Z",
                "source": "manual_fixture",
                "publisher": "Fixture Newswire",
                "title": "Apple expands services coverage",
                "summary": "Deterministic fixture headline for AAPL news planning.",
                "url": "https://example.com/news/aapl-1",
                "tickers": ("AAPL",),
                "sentiment_label": "positive",
                "sentiment_score": 0.72,
                "raw_source_id": "fixture-aapl-1",
                "notes": "deterministic fixture",
            }
        )
        self.assertEqual(record.news_id, "news-aapl-2026-05-30-01")
        self.assertEqual(record.published_at, "2026-05-30T14:30:00Z")
        self.assertEqual(record.source, "manual_fixture")
        self.assertEqual(record.publisher, "Fixture Newswire")
        self.assertEqual(record.title, "Apple expands services coverage")
        self.assertEqual(record.summary, "Deterministic fixture headline for AAPL news planning.")
        self.assertEqual(record.url, "https://example.com/news/aapl-1")
        self.assertEqual(record.tickers, ("AAPL",))
        self.assertEqual(record.sentiment_label, "positive")
        self.assertEqual(record.sentiment_score, 0.72)
        self.assertEqual(record.raw_source_id, "fixture-aapl-1")
        self.assertEqual(record.notes, "deterministic fixture")

    def test_dry_run_output(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main([])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("record_count=3", printed)
        self.assertIn("normalized_count=3", printed)
        self.assertIn("valid_count=3", printed)
        self.assertIn("invalid_count=0", printed)
        self.assertIn("tickers=['AAPL', 'MSFT', 'NVDA']", printed)
        self.assertIn("sources=['manual_fixture']", printed)
        self.assertIn("no_vendor_calls=True", printed)
        self.assertIn("no_db_reads=True", printed)
        self.assertIn("no_db_writes=True", printed)

    def test_ticker_filter(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main(["--ticker", "AAPL"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("record_count=1", printed)
        self.assertIn("tickers=['AAPL']", printed)

    def test_source_filter(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main(["--source", "manual_fixture"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("record_count=3", printed)
        self.assertIn("sources=['manual_fixture']", printed)

    def test_show_records_and_invalid(self) -> None:
        mod = self._module()
        with patch("builtins.print") as print_mock:
            mod.main(["--show-records", "--show-invalid"])
        printed = "\n".join(" ".join(str(arg) for arg in call.args) for call in print_mock.mock_calls)
        self.assertIn("records=(", printed)
        self.assertIn("invalid_records=(", printed)

    def test_no_forbidden_imports(self) -> None:
        text = Path("scripts/dry_run_news_sentiment.py").read_text(encoding="utf-8")
        self.assertNotIn("FastAPI", text)
        self.assertNotIn("APIRouter", text)
        self.assertNotIn("alembic", text.lower())
        self.assertNotIn("requests", text.lower())
        self.assertNotIn("httpx", text.lower())
        self.assertNotIn("DATABASE_URL", text)

    def test_docs_coverage(self) -> None:
        text = Path("docs/news_sentiment_foundation.md").read_text(encoding="utf-8").lower()
        self.assertIn("news/sentiment foundation", text)
        self.assertIn("news_id", text)
        self.assertIn("published_at", text)
        self.assertIn("sentiment_label", text)
        self.assertIn("sentiment_score", text)
        self.assertIn("raw_source_id", text)
        self.assertIn("no vendor calls", text)
        self.assertIn("no db writes", text)
        manual_doc = Path("docs/manual_ingestion_command_verification.md").read_text(encoding="utf-8").lower()
        self.assertIn("scripts.dry_run_news_sentiment", manual_doc)
