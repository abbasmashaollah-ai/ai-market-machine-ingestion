"""Dry-run aggregator for the core market feature bundle."""

from __future__ import annotations

from datetime import date, datetime, timezone

from app.features.breadth.breadth_job import run_breadth_dry_run
from app.features.cross_asset.cross_asset_job import run_cross_asset_dry_run
from app.features.event_calendar.event_calendar_job import run_event_calendar_dry_run
from app.features.liquidity_rates.liquidity_rates_job import run_liquidity_rates_dry_run
from app.features.news_sentiment.news_sentiment_job import run_news_sentiment_dry_run
from app.features.earnings.earnings_job import run_earnings_dry_run
from app.features.fundamentals.fundamentals_job import run_fundamentals_dry_run
from app.features.macro_liquidity.macro_liquidity_job import run_macro_liquidity_dry_run
from app.features.market_risk.market_risk_job import run_market_risk_dry_run
from app.features.flows_positioning.flows_positioning_job import run_flows_positioning_dry_run
from app.features.options.options_job import run_options_dry_run
from app.features.prices.price_feature_job import run_price_feature_dry_run
from app.features.volatility.volatility_job import run_volatility_dry_run
from app.features.sector_rotation.sector_rotation_reader import run_sector_rotation_certified_ohlcv_dry_run
from app.features.sector_rotation.sector_rotation_report import build_sector_rotation_dry_run_report
from app.features.market_features.fixtures.breadth_fixtures import build_breadth_fixture_histories_scenario
from app.features.market_features.fixtures.cross_asset_fixtures import build_cross_asset_fixture_histories_scenario
from app.features.market_features.fixtures.event_calendar_fixtures import build_event_calendar_fixture_events_scenario
from app.features.market_features.fixtures.liquidity_rates_fixtures import build_liquidity_rates_series_scenario
from app.features.market_features.fixtures.news_sentiment_fixtures import build_news_sentiment_fixture_articles_scenario
from app.features.market_features.fixtures.earnings_fixtures import build_earnings_fixture_scenario
from app.features.market_features.fixtures.fundamentals_fixtures import build_fundamentals_fixture_financials_scenario
from app.features.market_features.fixtures.flows_positioning_fixtures import build_flows_positioning_fixture_payload_scenario
from app.features.market_features.fixtures.options_fixtures import build_options_fixture_metrics_scenario
from app.features.market_features.fixtures.price_fixtures import build_price_ohlcv_fixtures
from app.features.market_features.fixtures.sector_rotation_fixtures import build_fake_data_read_client_for_sector_rotation
from app.features.market_features.fixtures.volatility_fixtures import build_volatility_series_scenario
from app.features.market_features.market_feature_bundle_summary import build_market_feature_bundle_summary


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


def _warnings_from_sections(*sections) -> list[str]:
    warnings: list[str] = []
    for section in sections:
        warnings.extend(list(section.warnings))
    return warnings


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

    event_calendar_events = build_event_calendar_fixture_events_scenario("fed_cpi_week")
    event_calendar_result = run_event_calendar_dry_run(
        event_calendar_events,
        observation_date=observation_date,
        timestamp=normalized_timestamp,
    )
    event_calendar_report = dict(event_calendar_result.reports[0]) if event_calendar_result.reports else {}
    event_calendar_section = {
        "report": event_calendar_report,
        "accepted_count": event_calendar_result.accepted_count,
        "rejected_count": event_calendar_result.rejected_count,
        "event_risk_label": event_calendar_report.get("event_risk_label"),
        "warnings": list(event_calendar_result.warnings),
        "no_db_writes": True,
        "no_vendor_calls": True,
        "no_live_api_calls": True,
        "no_scheduler_activation": True,
    }

    news_sentiment_articles = build_news_sentiment_fixture_articles_scenario("mixed_market")
    news_sentiment_result = run_news_sentiment_dry_run(
        news_sentiment_articles,
        observation_date=observation_date,
        timestamp=normalized_timestamp,
    )
    news_sentiment_report = dict(news_sentiment_result.reports[0]) if news_sentiment_result.reports else {}
    news_sentiment_section = {
        "report": news_sentiment_report,
        "accepted_count": news_sentiment_result.accepted_count,
        "rejected_count": news_sentiment_result.rejected_count,
        "sentiment_regime_label": news_sentiment_report.get("sentiment_regime_label"),
        "warnings": list(news_sentiment_result.warnings),
        "no_db_writes": True,
        "no_vendor_calls": True,
        "no_live_api_calls": True,
        "no_scheduler_activation": True,
    }

    earnings_payloads = build_earnings_fixture_scenario("mixed_earnings")
    earnings_result = run_earnings_dry_run(
        earnings_payloads,
        observation_date=observation_date,
        timestamp=normalized_timestamp,
    )
    earnings_reports = [dict(report) for report in earnings_result.reports]
    earnings_reports_by_symbol = {
        str(report.get("symbol", "")).upper(): report
        for report in earnings_reports
        if str(report.get("symbol", "")).strip()
    }
    earnings_section = {
        "reports": earnings_reports,
        "reports_by_symbol": earnings_reports_by_symbol,
        "accepted_count": earnings_result.accepted_count,
        "rejected_count": earnings_result.rejected_count,
        "earnings_regime_labels_by_symbol": {
            symbol: report.get("earnings_regime_label")
            for symbol, report in earnings_reports_by_symbol.items()
        },
        "warnings": list(earnings_result.warnings),
        "no_db_writes": True,
        "no_vendor_calls": True,
        "no_live_api_calls": True,
        "no_scheduler_activation": True,
    }

    fundamentals_financials = build_fundamentals_fixture_financials_scenario("mixed_quality")
    fundamentals_result = run_fundamentals_dry_run(
        fundamentals_financials,
        observation_date=observation_date,
        timestamp=normalized_timestamp,
    )
    fundamentals_reports = [dict(report) for report in fundamentals_result.reports]
    fundamentals_reports_by_symbol = {str(report.get("symbol", "")).upper(): report for report in fundamentals_reports if str(report.get("symbol", "")).strip()}
    fundamentals_section = {
        "reports": fundamentals_reports,
        "reports_by_symbol": fundamentals_reports_by_symbol,
        "accepted_count": fundamentals_result.accepted_count,
        "rejected_count": fundamentals_result.rejected_count,
        "fundamental_quality_labels_by_symbol": {
            symbol: report.get("fundamental_quality_label")
            for symbol, report in fundamentals_reports_by_symbol.items()
        },
        "warnings": list(fundamentals_result.warnings),
        "no_db_writes": True,
        "no_vendor_calls": True,
        "no_live_api_calls": True,
        "no_scheduler_activation": True,
    }

    flows_positioning_payload = build_flows_positioning_fixture_payload_scenario("mixed_positioning")
    flows_positioning_result = run_flows_positioning_dry_run(
        flows_positioning_payload,
        observation_date=observation_date,
        timestamp=normalized_timestamp,
    )
    flows_positioning_report = dict(flows_positioning_result.reports[0]) if flows_positioning_result.reports else {}
    flows_positioning_section = {
        "report": flows_positioning_report,
        "accepted_count": flows_positioning_result.accepted_count,
        "rejected_count": flows_positioning_result.rejected_count,
        "flow_regime_label": flows_positioning_report.get("flow_regime_label"),
        "warnings": list(flows_positioning_result.warnings),
        "no_db_writes": True,
        "no_vendor_calls": True,
        "no_live_api_calls": True,
        "no_scheduler_activation": True,
    }

    options_metrics = build_options_fixture_metrics_scenario("mixed_options")
    options_result = run_options_dry_run(
        next(iter(options_metrics.values())),
        observation_date=observation_date,
        timestamp=normalized_timestamp,
    )
    options_reports = [dict(report) for report in options_result.reports]
    options_reports_by_symbol = {
        str(report.get("symbol", "")).upper(): report
        for report in options_reports
        if str(report.get("symbol", "")).strip()
    }
    options_section = {
        "report": options_reports[0] if options_reports else {},
        "reports": options_reports,
        "reports_by_symbol": options_reports_by_symbol,
        "accepted_count": options_result.accepted_count,
        "rejected_count": options_result.rejected_count,
        "options_regime_label": (options_reports[0] if options_reports else {}).get("options_regime_label"),
        "options_regime_labels_by_symbol": {
            symbol: report.get("options_regime_label")
            for symbol, report in options_reports_by_symbol.items()
        },
        "warnings": list(options_result.warnings),
        "no_db_writes": True,
        "no_vendor_calls": True,
        "no_live_api_calls": True,
        "no_scheduler_activation": True,
    }

    base_bundle = {
        "observation_date": str(observation_date),
        "timestamp": normalized_timestamp,
        "prices": price_section,
        "breadth": breadth_section,
        "sector_rotation": sector_section,
        "cross_asset": cross_section,
        "liquidity_rates": liquidity_section,
        "volatility": volatility_section,
        "event_calendar": event_calendar_section,
        "news_sentiment": news_sentiment_section,
        "earnings": earnings_section,
        "fundamentals": fundamentals_section,
        "flows_positioning": flows_positioning_section,
        "options": options_section,
        "warnings": _warnings_from_sections(
            price_result,
            breadth_result,
            sector_result,
            cross_result,
            liquidity_result,
            volatility_result,
            event_calendar_result,
            news_sentiment_result,
            earnings_result,
            fundamentals_result,
            flows_positioning_result,
            options_result,
        ),
        "no_db_writes": True,
        "no_vendor_calls": True,
        "no_live_api_calls": True,
        "no_scheduler_activation": True,
    }

    macro_liquidity_summary = build_market_feature_bundle_summary(base_bundle)
    macro_liquidity_result = run_macro_liquidity_dry_run(
        macro_liquidity_summary,
        observation_date=observation_date,
        timestamp=normalized_timestamp,
    )
    macro_liquidity_report = dict(macro_liquidity_result.reports[0]) if macro_liquidity_result.reports else {}
    macro_liquidity_section = {
        "report": macro_liquidity_report,
        "accepted_count": macro_liquidity_result.accepted_count,
        "rejected_count": macro_liquidity_result.rejected_count,
        "macro_liquidity_label": macro_liquidity_report.get("macro_liquidity_label"),
        "warnings": list(macro_liquidity_result.warnings),
        "no_db_writes": True,
        "no_vendor_calls": True,
        "no_live_api_calls": True,
        "no_scheduler_activation": True,
    }

    final_bundle = dict(base_bundle)
    final_bundle["macro_liquidity"] = macro_liquidity_section
    risk_summary = build_market_feature_bundle_summary(final_bundle)
    market_risk_result = run_market_risk_dry_run(
        risk_summary,
        observation_date=observation_date,
        timestamp=normalized_timestamp,
    )
    market_risk_report = dict(market_risk_result.reports[0]) if market_risk_result.reports else {}
    market_risk_section = {
        "report": market_risk_report,
        "accepted_count": market_risk_result.accepted_count,
        "rejected_count": market_risk_result.rejected_count,
        "market_risk_label": market_risk_report.get("market_risk_label"),
        "warnings": list(market_risk_result.warnings),
        "no_db_writes": True,
        "no_vendor_calls": True,
        "no_live_api_calls": True,
        "no_scheduler_activation": True,
    }
    final_bundle["market_risk"] = market_risk_section
    final_bundle["warnings"] = list(base_bundle["warnings"]) + list(macro_liquidity_result.warnings) + list(market_risk_result.warnings)
    return final_bundle
