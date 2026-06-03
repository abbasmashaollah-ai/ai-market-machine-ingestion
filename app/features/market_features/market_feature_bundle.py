"""Dry-run aggregator for the core market feature bundle."""

from __future__ import annotations

from datetime import date, datetime, timezone

from app.features.breadth.breadth_job import run_breadth_dry_run
from app.features.cross_asset.cross_asset_job import run_cross_asset_dry_run
from app.features.liquidity_rates.liquidity_rates_job import run_liquidity_rates_dry_run
from app.features.prices.price_feature_job import run_price_feature_dry_run
from app.features.volatility.volatility_job import run_volatility_dry_run
from app.features.sector_rotation.sector_rotation_reader import run_sector_rotation_certified_ohlcv_dry_run
from app.features.sector_rotation.sector_rotation_report import build_sector_rotation_dry_run_report
from app.features.market_features.fixtures.breadth_fixtures import build_breadth_fixture_histories_scenario
from app.features.market_features.fixtures.cross_asset_fixtures import build_cross_asset_fixture_histories_scenario
from app.features.market_features.fixtures.liquidity_rates_fixtures import build_liquidity_rates_series_scenario
from app.features.market_features.fixtures.price_fixtures import build_price_ohlcv_fixtures
from app.features.market_features.fixtures.sector_rotation_fixtures import build_fake_data_read_client_for_sector_rotation
from app.features.market_features.fixtures.volatility_fixtures import build_volatility_series_scenario


def _normalize_timestamp(value: date | datetime | str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _reports_by_symbol(feature_result) -> dict[str, dict[str, object]]:
    reports_by_symbol: dict[str, dict[str, object]] = {}
    for report in getattr(feature_result, "reports", ()):
        symbol = str(report.get("symbol", "")).upper()
        if symbol:
            reports_by_symbol[symbol] = dict(report)
    return reports_by_symbol


def run_market_feature_bundle_dry_run(observation_date, timestamp=None):
    normalized_timestamp = _normalize_timestamp(timestamp)

    price_histories = build_price_ohlcv_fixtures()
    price_result = run_price_feature_dry_run(price_histories, observation_date, timestamp=normalized_timestamp)
    price_section = {
        "accepted_count": price_result.accepted_count,
        "rejected_count": price_result.rejected_count,
        "reports_by_symbol": _reports_by_symbol(price_result),
        "reports": [dict(report) for report in price_result.reports],
        "warnings": list(price_result.warnings),
        "no_db_writes": True,
        "no_vendor_calls": True,
        "no_live_api_calls": True,
        "no_scheduler_activation": True,
    }

    breadth_close_histories, breadth_volume_histories = build_breadth_fixture_histories_scenario("broad_strength")
    breadth_result = run_breadth_dry_run(
        breadth_close_histories,
        breadth_volume_histories,
        universe="SP500",
        observation_date=observation_date,
        timestamp=normalized_timestamp,
    )
    breadth_report = dict(breadth_result.reports[0]) if breadth_result.reports else {}
    breadth_section = {
        "report": breadth_report,
        "accepted_count": breadth_result.accepted_count,
        "rejected_count": breadth_result.rejected_count,
        "participation_label": breadth_report.get("participation_label"),
        "warnings": list(breadth_result.warnings),
        "no_db_writes": True,
        "no_vendor_calls": True,
        "no_live_api_calls": True,
        "no_scheduler_activation": True,
    }

    sector_client = build_fake_data_read_client_for_sector_rotation()
    sector_result = run_sector_rotation_certified_ohlcv_dry_run(
        sector_client,
        observation_date=observation_date,
        timestamp=normalized_timestamp,
    )
    sector_report = build_sector_rotation_dry_run_report(sector_result)
    sector_section = {
        "report": sector_report,
        "accepted_observation_count": sector_report.get("accepted_observation_count"),
        "accepted_summary_count": sector_report.get("accepted_summary_count"),
        "rejected_observation_count": sector_report.get("rejected_observation_count"),
        "rejected_summary_count": sector_report.get("rejected_summary_count"),
        "descriptive_rotation_state": sector_report.get("descriptive_rotation_state"),
        "warnings": list(sector_result.warnings),
        "no_db_writes": True,
        "no_vendor_calls": True,
        "no_live_api_calls": True,
        "no_scheduler_activation": True,
    }

    cross_close_histories, _ = build_cross_asset_fixture_histories_scenario("risk_on")
    cross_result = run_cross_asset_dry_run(
        cross_close_histories,
        observation_date=observation_date,
        timestamp=normalized_timestamp,
    )
    cross_report = dict(cross_result.reports[0]) if cross_result.reports else {}
    cross_section = {
        "report": cross_report,
        "accepted_count": cross_result.accepted_count,
        "rejected_count": cross_result.rejected_count,
        "descriptive_intermarket_state": cross_report.get("descriptive_intermarket_state"),
        "warnings": list(cross_result.warnings),
        "no_db_writes": True,
        "no_vendor_calls": True,
        "no_live_api_calls": True,
        "no_scheduler_activation": True,
    }

    liquidity_histories = build_liquidity_rates_series_scenario("liquidity_tailwind")
    liquidity_result = run_liquidity_rates_dry_run(
        liquidity_histories,
        observation_date=observation_date,
        timestamp=normalized_timestamp,
    )
    liquidity_report = dict(liquidity_result.reports[0]) if liquidity_result.reports else {}
    liquidity_section = {
        "report": liquidity_report,
        "accepted_count": liquidity_result.accepted_count,
        "rejected_count": liquidity_result.rejected_count,
        "liquidity_regime_label": liquidity_report.get("liquidity_regime_label"),
        "warnings": list(liquidity_result.warnings),
        "no_db_writes": True,
        "no_vendor_calls": True,
        "no_live_api_calls": True,
        "no_scheduler_activation": True,
    }

    volatility_histories = build_volatility_series_scenario("mixed_volatility")
    volatility_result = run_volatility_dry_run(
        volatility_histories,
        observation_date=observation_date,
        timestamp=normalized_timestamp,
    )
    volatility_report = dict(volatility_result.reports[0]) if volatility_result.reports else {}
    volatility_section = {
        "report": volatility_report,
        "accepted_count": volatility_result.accepted_count,
        "rejected_count": volatility_result.rejected_count,
        "volatility_regime_label": volatility_report.get("volatility_regime_label"),
        "warnings": list(volatility_result.warnings),
        "no_db_writes": True,
        "no_vendor_calls": True,
        "no_live_api_calls": True,
        "no_scheduler_activation": True,
    }

    return {
        "observation_date": str(observation_date),
        "timestamp": normalized_timestamp,
        "prices": price_section,
        "breadth": breadth_section,
        "sector_rotation": sector_section,
        "cross_asset": cross_section,
        "liquidity_rates": liquidity_section,
        "volatility": volatility_section,
        "warnings": list(price_result.warnings)
        + list(breadth_result.warnings)
        + list(sector_result.warnings)
        + list(cross_result.warnings)
        + list(liquidity_result.warnings)
        + list(volatility_result.warnings),
        "no_db_writes": True,
        "no_vendor_calls": True,
        "no_live_api_calls": True,
        "no_scheduler_activation": True,
    }
