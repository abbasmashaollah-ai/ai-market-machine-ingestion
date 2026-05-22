import unittest

from app.writers.canonical_writer import WriteStatus, WriterResult, summarize_writer_results
from app.writers.lineage_writer import LineageWriter
from app.writers.macro_writer import MacroWriter
from app.writers.ohlcv_writer import OhlcvWriter
from app.writers.symbol_writer import SymbolWriter


class WriterContractTests(unittest.TestCase):
    def test_writer_result_shape(self) -> None:
        result = WriterResult(writer_name="test", status=WriteStatus.SUCCESS, written_count=2)
        self.assertTrue(result.succeeded)
        self.assertEqual(result.written_count, 2)

    def test_batch_summary_helper(self) -> None:
        summary = summarize_writer_results(
            [
                WriterResult(writer_name="a", status=WriteStatus.SUCCESS, written_count=1),
                WriterResult(writer_name="b", status=WriteStatus.FAILURE, failed_count=1),
            ]
        )
        self.assertEqual(summary.total_writers, 2)
        self.assertEqual(summary.successful_writers, 1)
        self.assertEqual(summary.failed_writers, 1)

    def test_placeholder_writers_raise_not_implemented(self) -> None:
        self.assertEqual(OhlcvWriter().write([]).status, WriteStatus.SKIPPED)
        with self.assertRaises(NotImplementedError):
            MacroWriter().write([])
        with self.assertRaises(NotImplementedError):
            SymbolWriter().write([])
        with self.assertRaises(NotImplementedError):
            LineageWriter().write([])
