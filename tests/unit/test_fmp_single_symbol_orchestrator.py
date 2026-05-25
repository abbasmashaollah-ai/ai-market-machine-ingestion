import unittest
from datetime import date
from pathlib import Path
from unittest.mock import Mock

from app.ingestion.ohlcv.orchestrator import FmpOhlcvIngestionRequest, build_single_symbol_ohlcv_write_plan
from app.vendors.common.http import HttpResponse, ResponseMetadata
from app.vendors.fmp.client import FmpClientConfig, UnsupportedFmpClient


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
        self.assertEqual(plan.status, "completed")
        self.assertEqual(plan.normalized_records[0].symbol, "AAPL")
        self.assertEqual(plan.lineage_evidence["dataset"], "ohlcv")
        self.assertEqual(plan.lineage_evidence["row_count"], 1)
        self.assertEqual(plan.lineage_evidence["did_write_db"], False)
        self.assertEqual(plan.checkpoint_plan["checkpoint_id"], "fmp:ohlcv:AAPL:1d:2026-01-02:2026-01-02")
        self.assertEqual(plan.checkpoint_plan["metadata"]["checkpoint_persistence"], "not_implemented")
        self.assertEqual(plan.errors, ())

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
