import unittest
from datetime import date
from pathlib import Path
from unittest.mock import Mock

from app.ingestion.ohlcv.fanout import (
    FmpMultiSymbolOhlcvFanoutRequest,
    build_multi_symbol_ohlcv_fanout,
)
from app.ingestion.ohlcv.orchestrator import FmpOhlcvIngestionPlan


def _plan(
    *,
    symbol: str,
    raw_record_count: int = 1,
    normalized_record_count: int = 1,
    did_write_db: bool = False,
    status: str = "completed",
    writer_execution_performed: bool = False,
    writer_errors: tuple[dict[str, object], ...] = (),
    checkpoint_persistence_performed: bool = False,
    checkpoint_errors: tuple[dict[str, object], ...] = (),
) -> FmpOhlcvIngestionPlan:
    return FmpOhlcvIngestionPlan(
        vendor="fmp",
        symbol=symbol,
        timeframe="1d",
        requested_start_date=date(2026, 1, 2),
        requested_end_date=date(2026, 1, 3),
        raw_record_count=raw_record_count,
        normalized_record_count=normalized_record_count,
        did_write_db=did_write_db,
        intended_target="canonical_ohlcv",
        write_mode="dry_run",
        checkpoint_persistence_requested=checkpoint_persistence_performed,
        checkpoint_persistence_performed=checkpoint_persistence_performed,
        checkpoint_result=None,
        checkpoint_errors=checkpoint_errors,
        writer_execution_requested=writer_execution_performed,
        writer_execution_performed=writer_execution_performed,
        writer_handoff_ready=True,
        intended_writer_target="canonical_ohlcv",
        writer_payload_preview={"record_count": normalized_record_count},
        writer_result=None,
        writer_errors=writer_errors,
        errors=(),
        status=status,
    )


class FmpMultiSymbolOhlcvFanoutTests(unittest.TestCase):
    def test_default_dry_run_fanout_aggregates_per_symbol_results(self) -> None:
        orchestrator = Mock(side_effect=[_plan(symbol="AAPL"), _plan(symbol="MSFT")])

        result = build_multi_symbol_ohlcv_fanout(
            FmpMultiSymbolOhlcvFanoutRequest(
                symbols=("AAPL", "MSFT"),
                start_date=date(2026, 1, 2),
                end_date=date(2026, 1, 3),
            ),
            symbol_orchestrator=orchestrator,
        )

        self.assertEqual(result.requested_symbols, ("AAPL", "MSFT"))
        self.assertEqual(result.completed_symbols, ("AAPL", "MSFT"))
        self.assertEqual(result.failed_symbols, ())
        self.assertEqual(result.raw_record_count, 2)
        self.assertEqual(result.normalized_record_count, 2)
        self.assertFalse(result.did_write_db)
        self.assertEqual(result.writer_status, "not_requested")
        self.assertEqual(result.checkpoint_status, "not_requested")
        self.assertEqual(len(result.per_symbol_results), 2)
        self.assertEqual(result.per_symbol_results[0]["symbol"], "AAPL")
        self.assertEqual(result.per_symbol_results[1]["symbol"], "MSFT")
        self.assertEqual(orchestrator.call_count, 2)

    def test_one_symbol_failure_without_fail_fast_continues_remaining_symbols(self) -> None:
        orchestrator = Mock(
            side_effect=[
                _plan(symbol="AAPL", status="failed"),
                _plan(symbol="MSFT"),
            ]
        )

        result = build_multi_symbol_ohlcv_fanout(
            FmpMultiSymbolOhlcvFanoutRequest(
                symbols=("AAPL", "MSFT"),
                start_date=date(2026, 1, 2),
                end_date=date(2026, 1, 3),
            ),
            symbol_orchestrator=orchestrator,
            fail_fast=False,
        )

        self.assertEqual(result.completed_symbols, ("MSFT",))
        self.assertEqual(result.failed_symbols, ("AAPL",))
        self.assertEqual(len(result.per_symbol_results), 2)
        self.assertEqual(orchestrator.call_count, 2)

    def test_fail_fast_stops_after_first_failure(self) -> None:
        orchestrator = Mock(side_effect=[_plan(symbol="AAPL", status="failed"), _plan(symbol="MSFT")])

        result = build_multi_symbol_ohlcv_fanout(
            FmpMultiSymbolOhlcvFanoutRequest(
                symbols=("AAPL", "MSFT"),
                start_date=date(2026, 1, 2),
                end_date=date(2026, 1, 3),
            ),
            symbol_orchestrator=orchestrator,
            fail_fast=True,
        )

        self.assertEqual(result.completed_symbols, ())
        self.assertEqual(result.failed_symbols, ("AAPL",))
        self.assertEqual(len(result.per_symbol_results), 1)
        self.assertEqual(orchestrator.call_count, 1)

    def test_explicit_writer_and_checkpoint_options_are_passed_through_only_when_requested(self) -> None:
        orchestrator = Mock(side_effect=[_plan(symbol="AAPL")])
        writer = Mock(name="writer")
        checkpoint_writer = Mock(name="checkpoint_writer")

        build_multi_symbol_ohlcv_fanout(
            FmpMultiSymbolOhlcvFanoutRequest(
                symbols=("AAPL",),
                start_date=date(2026, 1, 2),
                end_date=date(2026, 1, 3),
            ),
            symbol_orchestrator=orchestrator,
            writer=writer,
            checkpoint_writer=checkpoint_writer,
            execute_writer=False,
            execute_checkpoint_persistence=False,
        )

        kwargs = orchestrator.call_args.kwargs
        self.assertIsNone(kwargs["writer"])
        self.assertIsNone(kwargs["checkpoint_writer"])

        build_multi_symbol_ohlcv_fanout(
            FmpMultiSymbolOhlcvFanoutRequest(
                symbols=("AAPL",),
                start_date=date(2026, 1, 2),
                end_date=date(2026, 1, 3),
            ),
            symbol_orchestrator=orchestrator,
            writer=writer,
            checkpoint_writer=checkpoint_writer,
            execute_writer=True,
            execute_checkpoint_persistence=True,
        )

        kwargs = orchestrator.call_args.kwargs
        self.assertIs(kwargs["writer"], writer)
        self.assertIs(kwargs["checkpoint_writer"], checkpoint_writer)

    def test_aggregate_did_write_db_reflects_symbol_results(self) -> None:
        orchestrator = Mock(side_effect=[_plan(symbol="AAPL", did_write_db=True), _plan(symbol="MSFT", did_write_db=False)])

        result = build_multi_symbol_ohlcv_fanout(
            FmpMultiSymbolOhlcvFanoutRequest(
                symbols=("AAPL", "MSFT"),
                start_date=date(2026, 1, 2),
                end_date=date(2026, 1, 3),
            ),
            symbol_orchestrator=orchestrator,
        )

        self.assertTrue(result.did_write_db)

    def test_aggregate_writer_and_checkpoint_status_reflect_symbol_plans(self) -> None:
        orchestrator = Mock(
            side_effect=[
                _plan(
                    symbol="AAPL",
                    did_write_db=True,
                    writer_execution_performed=True,
                    checkpoint_persistence_performed=True,
                ),
                _plan(symbol="MSFT"),
            ]
        )

        result = build_multi_symbol_ohlcv_fanout(
            FmpMultiSymbolOhlcvFanoutRequest(
                symbols=("AAPL", "MSFT"),
                start_date=date(2026, 1, 2),
                end_date=date(2026, 1, 3),
            ),
            symbol_orchestrator=orchestrator,
        )

        self.assertEqual(result.writer_status, "completed")
        self.assertEqual(result.checkpoint_status, "completed")

    def test_source_boundary_has_no_data_repo_imports(self) -> None:
        for relative_path in (
            "app/ingestion/ohlcv/fanout.py",
            "app/ingestion/ohlcv/__init__.py",
        ):
            source = Path(relative_path).read_text(encoding="utf-8")
            self.assertNotIn("ai-market-machine-data", source, msg=relative_path)
            self.assertNotIn("ai_market_machine_data", source, msg=relative_path)
