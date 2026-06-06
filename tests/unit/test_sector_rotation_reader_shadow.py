from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.clients.data_read_client import MarketFeatureBundleReadResult
from app.features.sector_rotation.sector_rotation_reader import (
    build_price_history_by_symbol,
    build_sector_rotation_shadow_diagnostic,
    fetch_sector_rotation_price_history,
    run_sector_rotation_certified_ohlcv_dry_run,
)
from app.features.sector_rotation.sector_universe import get_required_symbols


def _row(symbol: str, day: int, close: float, **kwargs: object) -> dict[str, object]:
    payload = {
        "symbol": symbol,
        "date": datetime(2026, 1, day, tzinfo=timezone.utc),
        "close": close,
        "quality_status": "VALID",
        "certification_status": "CERTIFIED",
        "freshness_status": "FRESH",
        "source": "canonical_ohlcv",
        "lineage": {"source": "fixture"},
    }
    payload.update(kwargs)
    return payload


def _full_fixture_rows(history_length: int = 90) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for offset, symbol in enumerate(get_required_symbols(), start=1):
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        for day in range(history_length):
            rows.append(_row(symbol, 1, 100.0 + offset + day / 100.0, date=base + timedelta(days=day)))
    return rows


class FakeSectorRotationClient:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows
        self.calls: list[dict[str, object]] = []

    def get_symbol_ohlcv_history(self, symbol, start_date=None, end_date=None, limit=None, order="asc"):
        self.calls.append(
            {
                "symbol": str(symbol).upper(),
                "start_date": start_date,
                "end_date": end_date,
                "limit": limit,
                "order": order,
            }
        )
        normalized_symbol = str(symbol).upper()
        filtered = [row for row in self.rows if str(row.get("symbol", "")).upper() == normalized_symbol]
        return {"historical_ohlcv": filtered, "warnings": []}


class FakeMarketFeatureBundleClient:
    def __init__(self, result: MarketFeatureBundleReadResult) -> None:
        self.result = result
        self.calls: list[str] = []

    def get_market_feature_bundle(self, universe: str) -> MarketFeatureBundleReadResult:
        self.calls.append(str(universe).upper())
        return self.result


def _bundle_result(**overrides: object) -> MarketFeatureBundleReadResult:
    payload = {
        "universe": "SPY",
        "evidence_available": True,
        "dataset_version": "production_pilot.v1",
        "schema_version": "market_feature_bundle.v1",
        "validation_status": "PASS",
        "certification_status": "CERTIFIED",
        "coverage_status": "COMPLETE",
        "quality_status": "PASS",
        "compact_summary": {
            "feature_sections_present": {
                "prices": True,
                "sector_rotation": True,
                "market_risk": True,
                "market_regime": True,
                "macro_liquidity": True,
                "flows_positioning": True,
            }
        },
        "full_bundle_payload": {"example": True},
        "idempotency_key_prefix": "abcdef123456",
    }
    payload.update(overrides)
    return MarketFeatureBundleReadResult(**payload)


def test_shadow_disabled_preserves_current_output_exactly() -> None:
    client = FakeSectorRotationClient(_full_fixture_rows())

    baseline = run_sector_rotation_certified_ohlcv_dry_run(
        client,
        observation_date="2026-01-15",
        timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc),
    )
    disabled = run_sector_rotation_certified_ohlcv_dry_run(
        client,
        observation_date="2026-01-15",
        timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc),
        enable_market_feature_bundle_shadow=False,
    )

    assert disabled == baseline
    assert disabled.shadow_diagnostic is None
    assert len(client.calls) == len(get_required_symbols(include_benchmark=True)) * 2


def test_shadow_enabled_uses_injected_bundle_client_without_altering_primary_result() -> None:
    sector_client = FakeSectorRotationClient(_full_fixture_rows())
    bundle_client = FakeMarketFeatureBundleClient(_bundle_result())

    result = run_sector_rotation_certified_ohlcv_dry_run(
        sector_client,
        observation_date="2026-01-15",
        timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc),
        enable_market_feature_bundle_shadow=True,
        market_feature_bundle_client=bundle_client,
    )

    assert bundle_client.calls == ["SPY"]
    assert result.shadow_diagnostic is not None
    assert result.shadow_diagnostic.enabled is True
    assert result.shadow_diagnostic.evidence_available is True
    assert result.shadow_diagnostic.universe == "SPY"
    assert result.shadow_diagnostic.dataset_version == "production_pilot.v1"
    assert result.shadow_diagnostic.schema_version == "market_feature_bundle.v1"
    assert result.shadow_diagnostic.certification_status == "CERTIFIED"
    assert result.shadow_diagnostic.validation_status == "PASS"
    assert result.shadow_diagnostic.coverage_status == "COMPLETE"
    assert result.shadow_diagnostic.quality_status == "PASS"
    assert result.dry_run_result is not None
    assert result.dry_run_result.writer_result.accepted_observation_count == 11
    assert result.dry_run_result.writer_result.accepted_summary_count == 1


def test_shadow_no_evidence_skips_comparison_without_changing_output() -> None:
    sector_client = FakeSectorRotationClient(_full_fixture_rows())
    bundle_client = FakeMarketFeatureBundleClient(
        _bundle_result(
            evidence_available=False,
            certification_status=None,
            validation_status=None,
            coverage_status=None,
            quality_status=None,
            compact_summary=None,
        )
    )

    result = run_sector_rotation_certified_ohlcv_dry_run(
        sector_client,
        observation_date="2026-01-15",
        timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc),
        enable_market_feature_bundle_shadow=True,
        market_feature_bundle_client=bundle_client,
    )

    assert bundle_client.calls == ["SPY"]
    assert result.shadow_diagnostic is not None
    assert result.shadow_diagnostic.evidence_available is False
    assert result.shadow_diagnostic.skipped is True
    assert result.dry_run_result is not None
    assert result.dry_run_result.writer_result.accepted_observation_count == 11
    assert result.dry_run_result.writer_result.accepted_summary_count == 1


def test_shadow_route_failure_skips_comparison_without_changing_output() -> None:
    sector_client = FakeSectorRotationClient(_full_fixture_rows())

    class RouteFailureBundleClient:
        def __init__(self) -> None:
            self.calls: list[str] = []

        def get_market_feature_bundle(self, universe: str):
            self.calls.append(str(universe).upper())
            raise RuntimeError("route failure")

    bundle_client = RouteFailureBundleClient()

    result = run_sector_rotation_certified_ohlcv_dry_run(
        sector_client,
        observation_date="2026-01-15",
        timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc),
        enable_market_feature_bundle_shadow=True,
        market_feature_bundle_client=bundle_client,
    )

    assert bundle_client.calls == ["SPY"]
    assert result.shadow_diagnostic is not None
    assert result.shadow_diagnostic.evidence_available is False
    assert result.shadow_diagnostic.route_failure is True
    assert result.dry_run_result is not None
    assert result.dry_run_result.writer_result.accepted_observation_count == 11
    assert result.dry_run_result.writer_result.accepted_summary_count == 1


def test_sector_rotation_reader_source_scan_has_no_db_vendor_write_or_decision_logic() -> None:
    text = Path("app/features/sector_rotation/sector_rotation_reader.py").read_text(encoding="utf-8").lower()
    assert "sqlalchemy" not in text
    assert "app.database" not in text
    assert "post(" not in text
    assert "put(" not in text
    assert "delete(" not in text
    assert "write(" not in text
    assert "judge posture" not in text
    assert "trading decision" not in text
    assert "risk posture" not in text
    assert "portfolio allocation" not in text
    assert "capital logic" not in text
    assert "execution logic" not in text


def test_protected_modules_remain_out_of_reader_scope() -> None:
    text = Path("app/features/sector_rotation/sector_rotation_reader.py").read_text(encoding="utf-8")
    for needle in [
        "app.features.market_risk",
        "app.features.market_regime",
        "app.features.macro_liquidity",
        "app.features.flows_positioning",
    ]:
        assert needle not in text
