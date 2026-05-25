from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import unittest
from unittest.mock import Mock

from app.ingestion.volatility.polygon import (
    POLYGON_VOLATILITY_SYMBOL_MAP,
    build_polygon_volatility_dry_run_plan,
    canonical_volatility_symbol_to_polygon_symbol,
    polygon_symbol_to_canonical_volatility_symbol,
    polygon_volatility_payload_to_canonical_record,
    validate_polygon_volatility_payload,
)


class PolygonVolatilityMappingTests(unittest.TestCase):
    def test_symbol_mapping_round_trip(self) -> None:
        self.assertEqual(canonical_volatility_symbol_to_polygon_symbol("VIX"), "I:VIX")
        self.assertEqual(canonical_volatility_symbol_to_polygon_symbol("vvix"), "I:VVIX")
        self.assertEqual(polygon_symbol_to_canonical_volatility_symbol("I:VXN"), "VXN")
        self.assertEqual(POLYGON_VOLATILITY_SYMBOL_MAP["RVX"], "I:RVX")

    def test_payload_validation_and_canonical_mapping(self) -> None:
        payload = {"ticker": "I:VIX", "t": 1735776000000, "o": 10, "h": 11, "l": 9, "c": 10.5, "v": 100}
        is_valid, errors = validate_polygon_volatility_payload(payload)
        record = polygon_volatility_payload_to_canonical_record(payload, symbol="VIX")

        self.assertTrue(is_valid)
        self.assertEqual(errors, ())
        self.assertEqual(record.symbol, "VIX")
        self.assertEqual(record.symbol_id, "I:VIX")
        self.assertEqual(record.vendor, "polygon")
        self.assertEqual(record.source, "polygon_aggregates")

    def test_invalid_payload_reports_errors(self) -> None:
        is_valid, errors = validate_polygon_volatility_payload({"ticker": "I:VIX"})

        self.assertFalse(is_valid)
        self.assertIn("t or date is required", errors)
        self.assertIn("o is required", errors)

    def test_dry_run_plan_defaults_to_no_fetch(self) -> None:
        plan = build_polygon_volatility_dry_run_plan(
            symbols=("VIX", "VVIX"),
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
        )

        self.assertTrue(plan.dry_run)
        self.assertFalse(plan.fetch_enabled)
        self.assertEqual(plan.total_payload_count, 0)
        self.assertEqual(plan.total_valid_count, 0)
        self.assertEqual(plan.total_invalid_count, 0)
        self.assertEqual(plan.status, "planned")
        self.assertEqual(tuple(plan.requested_symbols), ("VIX", "VVIX"))

    def test_dry_run_plan_uses_injected_fetch_adapter_when_enabled(self) -> None:
        adapter = Mock()
        adapter.fetch_aggregates_raw.return_value = [
            {"ticker": "I:VIX", "t": 1735776000000, "o": 10, "h": 11, "l": 9, "c": 10.5, "v": 100}
        ]

        plan = build_polygon_volatility_dry_run_plan(
            symbols=("VIX",),
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            fetch_adapter=adapter,
            fetch_enabled=True,
        )

        adapter.fetch_aggregates_raw.assert_called_once_with("I:VIX", from_date="2025-01-01", to_date="2025-01-31")
        self.assertEqual(plan.total_payload_count, 1)
        self.assertEqual(plan.total_valid_count, 1)
        self.assertEqual(plan.batch_errors, ())
        self.assertEqual(plan.symbol_plans[0].records[0].canonical_record.symbol, "VIX")

    def test_fetch_error_is_captured_as_batch_error(self) -> None:
        adapter = Mock()
        adapter.fetch_aggregates_raw.side_effect = RuntimeError("unavailable")

        plan = build_polygon_volatility_dry_run_plan(
            symbols=("VIX",),
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            fetch_adapter=adapter,
            fetch_enabled=True,
        )

        self.assertEqual(plan.status, "failed")
        self.assertEqual(plan.batch_errors[0]["kind"], "fetch_error")
        self.assertIn("unavailable", plan.batch_errors[0]["message"])

    def test_unsupported_symbol_is_reported(self) -> None:
        plan = build_polygon_volatility_dry_run_plan(
            symbols=("NOT_REAL",),
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
        )

        self.assertEqual(plan.status, "failed")
        self.assertEqual(plan.batch_errors[0]["kind"], "unsupported_symbol")
        self.assertEqual(plan.symbol_plans[0].status, "failed")

