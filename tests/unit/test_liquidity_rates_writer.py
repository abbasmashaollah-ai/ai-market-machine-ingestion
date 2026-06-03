from copy import deepcopy

from app.features.liquidity_rates.liquidity_rates_builder import build_liquidity_rates_observation
from app.features.liquidity_rates.liquidity_rates_writer import LiquidityRatesMockWriter, write_liquidity_rates_payloads
from tests.fixtures.liquidity_rates_series import build_liquidity_rates_series_fixtures


def test_writer_accepts_valid_rows() -> None:
    observation = build_liquidity_rates_observation(build_liquidity_rates_series_fixtures(), "2026-01-15")
    writer = LiquidityRatesMockWriter()
    result = write_liquidity_rates_payloads([observation], writer=writer)
    assert result.accepted_count == 1
    assert result.rejected_count == 0
    assert result.no_db_writes is True
    assert len(writer.accepted_rows) == 1


def test_writer_does_not_mutate_inputs() -> None:
    observation = build_liquidity_rates_observation(build_liquidity_rates_series_fixtures(), "2026-01-15")
    snapshot = deepcopy(observation)
    write_liquidity_rates_payloads([observation], writer=LiquidityRatesMockWriter())
    assert observation == snapshot