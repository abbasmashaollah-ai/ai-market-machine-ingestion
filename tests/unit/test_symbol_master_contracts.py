import unittest

from app.models.normalized import NormalizedSymbolRecord
from app.symbol_master.service import UnsupportedSymbolMasterService
from app.symbol_master.sync import build_symbol_sync_plan
from app.symbol_master.universe import UniverseName, build_universe_request
from app.symbol_master.validators import validate_symbol_record


class SymbolMasterContractTests(unittest.TestCase):
    def test_symbol_validation(self) -> None:
        record = NormalizedSymbolRecord(symbol="AAPL", symbol_id="sym-1", vendor="polygon", active=True)
        results = validate_symbol_record(record)
        self.assertTrue(all(result.passed for result in results))

    def test_invalid_symbol_records(self) -> None:
        record = NormalizedSymbolRecord(symbol=None, symbol_id="sym-1", vendor="", active="yes")  # type: ignore[arg-type]
        results = validate_symbol_record(record)
        self.assertTrue(any(not result.passed for result in results))

    def test_universe_request_shape(self) -> None:
        request = build_universe_request("us_equities", vendor="polygon", as_of="2026-01-01", symbols=("AAPL",))
        self.assertEqual(request.universe, UniverseName.US_EQUITIES)
        self.assertEqual(request.symbols, ("AAPL",))

    def test_sync_plan_shape(self) -> None:
        plan = build_symbol_sync_plan("etfs", vendor="polygon", expected_count=10, batch_size=5, symbols=("SPY",))
        self.assertEqual(plan.universe, "etfs")
        self.assertEqual(plan.batch_size, 5)

    def test_service_placeholder_boundary(self) -> None:
        service = UnsupportedSymbolMasterService()
        with self.assertRaises(NotImplementedError):
            service.sync()
