import unittest
from datetime import date
from pathlib import Path
from unittest.mock import Mock

from app.ingestion.ohlcv.orchestrator import (
    FmpOhlcvIngestionRequest,
    _required_writer_fields,
    build_single_symbol_ohlcv_write_plan,
)
from app.ingestion.ohlcv.normalization import normalize_fmp_ohlcv_record
from app.models.normalized import NormalizedOHLCVRecord
from app.vendors.common.http import HttpResponse, ResponseMetadata
from app.vendors.fmp.client import FmpClientConfig, UnsupportedFmpClient
from app.writers.canonical_writer import WriteStatus, WriterResult


class _RecordingWriter:
    def __init__(self, result: WriterResult) -> None:
        self.result = result
        self.calls: list[list[object]] = []

    def write(self, records: list[object]) -> WriterResult:
        self.calls.append(list(records))
        return self.result


class _RecordingCheckpointWriter:
    def __init__(self, result: object) -> None:
        self.result = result
        self.calls: list[dict[str, object]] = []

    def save(self, checkpoint: dict[str, object]) -> object:
        self.calls.append(dict(checkpoint))
        return self.result


class FmpSingleSymbolOrchestratorTests(unittest.TestCase):
    def test_write_plan_is_dry_run_and_includes_metadata(self) -> None:
        transport = Mock()
        transport.request.return_value = HttpResponse(
            metadata=ResponseMetadata(status_code=200, elapsed_seconds=0.1),
            text='{"historical": [{"date": "2026-01-02", "open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 12345}]}',
            json={"historical": [{"date": "2026-01-02", "open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 12345}]},
        )
        client = UnsupportedFmpClient(FmpClientConfig(api_key="secret"), http_client=transport)

        plan = build_single_symbol_ohlcv_write_plan(
            FmpOhlcvIngestionRequest(
                symbol="AAPL",
                start_date=date(2026, 1, 2),
                end_date=date(2026, 1, 2),
                api_key="secret",
            ),
            client=client,
        )

        self.assertEqual(plan.vendor, "fmp")
        self.assertEqual(plan.symbol, "AAPL")
        self.assertEqual(plan.raw_record_count, 1)
        self.assertEqual(plan.normalized_record_count, 1)
        self.assertFalse(plan.did_write_db)
        self.assertEqual(plan.intended_target, "canonical_ohlcv")
        self.assertEqual(plan.write_mode, "dry_run")
        self.assertFalse(plan.writer_execution_requested)
        self.assertFalse(plan.writer_execution_performed)
        self.assertTrue(plan.writer_handoff_ready)
        self.assertEqual(plan.intended_writer_target, "canonical_ohlcv")
        self.assertEqual(plan.writer_payload_preview["writer_name"], "ohlcv_writer")
        self.assertEqual(plan.writer_payload_preview["record_count"], 1)
        self.assertEqual(plan.status, "completed")
        self.assertEqual(plan.normalized_records[0].symbol, "AAPL")
        self.assertEqual(plan.lineage_evidence["dataset"], "ohlcv")
        self.assertEqual(plan.lineage_evidence["row_count"], 1)
        self.assertEqual(plan.lineage_evidence["did_write_db"], False)
        self.assertEqual(plan.checkpoint_plan["checkpoint_id"], "fmp:ohlcv:AAPL:1d:2026-01-02:2026-01-02")
        self.assertEqual(plan.checkpoint_plan["metadata"]["checkpoint_persistence"], "not_implemented")
        self.assertEqual(plan.errors, ())
        self.assertEqual(plan.writer_errors, ())
        self.assertIsNone(plan.writer_result)

    def test_orchestrator_classifies_vendor_fetch_errors(self) -> None:
        failing_client = Mock()
        from app.vendors.fmp.client import FmpFetchError, FmpFetchErrorKind

        failing_client.fetch_historical_ohlcv_raw.side_effect = FmpFetchError(
            FmpFetchErrorKind.TRANSIENT,
            "temporary failure",
            retryable=True,
        )

        plan = build_single_symbol_ohlcv_write_plan(
            FmpOhlcvIngestionRequest(
                symbol="AAPL",
                start_date=date(2026, 1, 2),
                end_date=date(2026, 1, 2),
                api_key="secret",
            ),
            client=failing_client,
        )

        self.assertEqual(plan.status, "failed")
        self.assertEqual(plan.normalized_record_count, 0)
        self.assertEqual(plan.errors[0]["kind"], "transient")
        self.assertTrue(plan.errors[0]["retryable"])
        self.assertFalse(plan.did_write_db)
        self.assertEqual(plan.writer_errors, ())
        self.assertIsNone(plan.writer_result)

    def test_writer_required_fields_validation(self) -> None:
        record = normalize_fmp_ohlcv_record(
            {
                "date": "2026-01-02",
                "open": 100,
                "high": 101,
                "low": 99,
                "close": 100.5,
                "volume": 12345,
            },
            symbol="AAPL",
        )

        preview = _required_writer_fields(record)

        self.assertEqual(preview["symbol"], "AAPL")
        self.assertEqual(preview["adjustment_status"], "unadjusted")
        self.assertEqual(preview["data_quality_status"], "pending")

    def test_injected_writer_mode_calls_writer_with_preview_payload(self) -> None:
        transport = Mock()
        transport.request.return_value = HttpResponse(
            metadata=ResponseMetadata(status_code=200, elapsed_seconds=0.1),
            text='{"historical": [{"date": "2026-01-02", "open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 12345}]}',
            json={"historical": [{"date": "2026-01-02", "open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 12345}]},
        )
        client = UnsupportedFmpClient(FmpClientConfig(api_key="secret"), http_client=transport)
        writer = _RecordingWriter(WriterResult(writer_name="ohlcv_writer", status=WriteStatus.SUCCESS, written_count=1))

        plan = build_single_symbol_ohlcv_write_plan(
            FmpOhlcvIngestionRequest(
                symbol="AAPL",
                start_date=date(2026, 1, 2),
                end_date=date(2026, 1, 2),
                api_key="secret",
            ),
            client=client,
            writer=writer,
            execute_writer=True,
        )

        self.assertTrue(plan.writer_execution_requested)
        self.assertTrue(plan.writer_execution_performed)
        self.assertTrue(plan.did_write_db)
        self.assertEqual(plan.writer_result["status"], "success")
        self.assertEqual(plan.writer_result["written_count"], 1)
        self.assertEqual(plan.writer_errors, ())
        self.assertEqual(len(writer.calls), 1)
        self.assertIsInstance(writer.calls[0][0], NormalizedOHLCVRecord)
        self.assertEqual(writer.calls[0][0].symbol, "AAPL")
        self.assertEqual(writer.calls[0][0].source, "fmp_historical_price_full")

    def test_injected_writer_failure_is_captured_and_not_marked_successful(self) -> None:
        transport = Mock()
        transport.request.return_value = HttpResponse(
            metadata=ResponseMetadata(status_code=200, elapsed_seconds=0.1),
            text='{"historical": [{"date": "2026-01-02", "open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 12345}]}',
            json={"historical": [{"date": "2026-01-02", "open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 12345}]},
        )
        client = UnsupportedFmpClient(FmpClientConfig(api_key="secret"), http_client=transport)

        class _FailingWriter:
            def write(self, records: list[object]) -> WriterResult:
                return WriterResult(writer_name="ohlcv_writer", status=WriteStatus.FAILURE, message="nope")

        plan = build_single_symbol_ohlcv_write_plan(
            FmpOhlcvIngestionRequest(
                symbol="AAPL",
                start_date=date(2026, 1, 2),
                end_date=date(2026, 1, 2),
                api_key="secret",
            ),
            client=client,
            writer=_FailingWriter(),
            execute_writer=True,
        )

        self.assertTrue(plan.writer_execution_requested)
        self.assertTrue(plan.writer_execution_performed)
        self.assertFalse(plan.did_write_db)
        self.assertEqual(plan.status, "failed")
        self.assertEqual(plan.writer_result["status"], "failure")
        self.assertEqual(plan.writer_errors[0]["kind"], "writer_failure")

    def test_default_mode_does_not_call_writer(self) -> None:
        transport = Mock()
        transport.request.return_value = HttpResponse(
            metadata=ResponseMetadata(status_code=200, elapsed_seconds=0.1),
            text='{"historical": [{"date": "2026-01-02", "open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 12345}]}',
            json={"historical": [{"date": "2026-01-02", "open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 12345}]},
        )
        client = UnsupportedFmpClient(FmpClientConfig(api_key="secret"), http_client=transport)
        writer = _RecordingWriter(WriterResult(writer_name="ohlcv_writer", status=WriteStatus.SUCCESS, written_count=1))

        plan = build_single_symbol_ohlcv_write_plan(
            FmpOhlcvIngestionRequest(
                symbol="AAPL",
                start_date=date(2026, 1, 2),
                end_date=date(2026, 1, 2),
                api_key="secret",
            ),
            client=client,
            writer=writer,
        )

        self.assertFalse(plan.writer_execution_requested)
        self.assertFalse(plan.writer_execution_performed)
        self.assertFalse(plan.did_write_db)
        self.assertEqual(writer.calls, [])

    def test_default_mode_does_not_call_checkpoint_writer(self) -> None:
        transport = Mock()
        transport.request.return_value = HttpResponse(
            metadata=ResponseMetadata(status_code=200, elapsed_seconds=0.1),
            text='{"historical": [{"date": "2026-01-02", "open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 12345}]}',
            json={"historical": [{"date": "2026-01-02", "open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 12345}]},
        )
        client = UnsupportedFmpClient(FmpClientConfig(api_key="secret"), http_client=transport)
        checkpoint_writer = _RecordingCheckpointWriter({"status": "saved"})

        plan = build_single_symbol_ohlcv_write_plan(
            FmpOhlcvIngestionRequest(
                symbol="AAPL",
                start_date=date(2026, 1, 2),
                end_date=date(2026, 1, 2),
                api_key="secret",
            ),
            client=client,
            checkpoint_writer=checkpoint_writer,
        )

        self.assertFalse(plan.checkpoint_persistence_requested)
        self.assertFalse(plan.checkpoint_persistence_performed)
        self.assertIsNone(plan.checkpoint_result)
        self.assertEqual(plan.checkpoint_errors, ())
        self.assertEqual(checkpoint_writer.calls, [])

    def test_injected_checkpoint_mode_calls_checkpoint_writer_with_plan_payload(self) -> None:
        transport = Mock()
        transport.request.return_value = HttpResponse(
            metadata=ResponseMetadata(status_code=200, elapsed_seconds=0.1),
            text='{"historical": [{"date": "2026-01-02", "open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 12345}]}',
            json={"historical": [{"date": "2026-01-02", "open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 12345}]},
        )
        client = UnsupportedFmpClient(FmpClientConfig(api_key="secret"), http_client=transport)
        checkpoint_writer = _RecordingCheckpointWriter({"checkpoint_id": "fmp:ohlcv:AAPL:1d:2026-01-02:2026-01-02", "status": "saved"})

        plan = build_single_symbol_ohlcv_write_plan(
            FmpOhlcvIngestionRequest(
                symbol="AAPL",
                start_date=date(2026, 1, 2),
                end_date=date(2026, 1, 2),
                api_key="secret",
            ),
            client=client,
            checkpoint_writer=checkpoint_writer,
            execute_checkpoint_persistence=True,
        )

        self.assertTrue(plan.checkpoint_persistence_requested)
        self.assertTrue(plan.checkpoint_persistence_performed)
        self.assertEqual(plan.checkpoint_result["status"], "saved")
        self.assertEqual(plan.checkpoint_errors, ())
        self.assertEqual(len(checkpoint_writer.calls), 1)
        self.assertEqual(checkpoint_writer.calls[0]["checkpoint_id"], "fmp:ohlcv:AAPL:1d:2026-01-02:2026-01-02")
        self.assertEqual(checkpoint_writer.calls[0]["metadata"]["checkpoint_persistence"], "not_implemented")
        self.assertIn("lineage_evidence", checkpoint_writer.calls[0])
        self.assertIn("writer_payload_preview", checkpoint_writer.calls[0])

    def test_checkpoint_writer_failure_is_captured(self) -> None:
        transport = Mock()
        transport.request.return_value = HttpResponse(
            metadata=ResponseMetadata(status_code=200, elapsed_seconds=0.1),
            text='{"historical": [{"date": "2026-01-02", "open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 12345}]}',
            json={"historical": [{"date": "2026-01-02", "open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 12345}]},
        )
        client = UnsupportedFmpClient(FmpClientConfig(api_key="secret"), http_client=transport)

        def _failing_checkpoint_writer(checkpoint: dict[str, object]) -> object:
            raise RuntimeError("checkpoint failed")

        plan = build_single_symbol_ohlcv_write_plan(
            FmpOhlcvIngestionRequest(
                symbol="AAPL",
                start_date=date(2026, 1, 2),
                end_date=date(2026, 1, 2),
                api_key="secret",
            ),
            client=client,
            checkpoint_writer=_failing_checkpoint_writer,
            execute_checkpoint_persistence=True,
        )

        self.assertTrue(plan.checkpoint_persistence_requested)
        self.assertTrue(plan.checkpoint_persistence_performed)
        self.assertIsNone(plan.checkpoint_result)
        self.assertEqual(plan.status, "failed")
        self.assertEqual(plan.checkpoint_errors[0]["kind"], "checkpoint_error")
        self.assertFalse(plan.did_write_db)

    def test_checkpoint_failure_does_not_mark_successful_ingestion(self) -> None:
        transport = Mock()
        transport.request.return_value = HttpResponse(
            metadata=ResponseMetadata(status_code=200, elapsed_seconds=0.1),
            text='{"historical": [{"date": "2026-01-02", "open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 12345}]}',
            json={"historical": [{"date": "2026-01-02", "open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 12345}]},
        )
        client = UnsupportedFmpClient(FmpClientConfig(api_key="secret"), http_client=transport)

        class _FailingCheckpointWriter:
            def save(self, checkpoint: dict[str, object]) -> object:
                raise RuntimeError("boom")

        plan = build_single_symbol_ohlcv_write_plan(
            FmpOhlcvIngestionRequest(
                symbol="AAPL",
                start_date=date(2026, 1, 2),
                end_date=date(2026, 1, 2),
                api_key="secret",
            ),
            client=client,
            checkpoint_writer=_FailingCheckpointWriter(),
            execute_checkpoint_persistence=True,
        )

        self.assertEqual(plan.status, "failed")
        self.assertFalse(plan.did_write_db)
        self.assertEqual(plan.checkpoint_errors[0]["kind"], "checkpoint_error")

    def test_source_boundary_has_no_data_repo_imports(self) -> None:
        for relative_path in (
            "app/vendors/fmp/client.py",
            "app/ingestion/ohlcv/normalization.py",
            "app/ingestion/ohlcv/orchestrator.py",
            "app/ingestion/ohlcv/single_symbol.py",
        ):
            source = Path(relative_path).read_text(encoding="utf-8")
            self.assertNotIn("ai-market-machine-data", source, msg=relative_path)
            self.assertNotIn("ai_market_machine_data", source, msg=relative_path)
