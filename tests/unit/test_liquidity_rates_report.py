import json

from app.features.liquidity_rates.liquidity_rates_builder import build_liquidity_rates_observation
from app.features.liquidity_rates.liquidity_rates_report import build_liquidity_rates_report
from app.features.liquidity_rates.liquidity_rates_writer import LiquidityRatesMockWriter, write_liquidity_rates_payloads
from tests.fixtures.liquidity_rates_series import build_liquidity_rates_series_fixtures


def test_report_contains_expected_fields() -> None:
    observation = build_liquidity_rates_observation(build_liquidity_rates_series_fixtures(), "2026-01-15")
    writer_result = write_liquidity_rates_payloads([observation], writer=LiquidityRatesMockWriter())
    report = build_liquidity_rates_report(observation, writer_result=writer_result)
    assert report["liquidity_regime_label"]
    assert report["accepted_count"] == 1
    assert report["no_db_writes"] is True
    json.dumps(report)