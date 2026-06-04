from copy import deepcopy

from app.features.options.options_builder import build_options_observation
from app.features.options.options_writer import OptionsMockWriter, write_options_payloads
from tests.fixtures.options_data import build_options_metrics_scenario


def test_mock_writer_accepts_valid_rows() -> None:
    observation = build_options_observation("NVDA", build_options_metrics_scenario("high_volatility")["NVDA"], "2026-01-15")
    writer = OptionsMockWriter()
    result = write_options_payloads([observation], writer=writer)
    assert result.accepted_count == 1
    assert result.rejected_count == 0
    assert result.no_db_writes is True


def test_mock_writer_preserves_input() -> None:
    observation = build_options_observation("NVDA", build_options_metrics_scenario("high_volatility")["NVDA"], "2026-01-15")
    snapshot = deepcopy(observation)
    write_options_payloads([observation], writer=OptionsMockWriter())
    assert observation == snapshot
