from copy import deepcopy

from app.features.volatility.volatility_builder import build_volatility_observation
from app.features.volatility.volatility_writer import VolatilityMockWriter, write_volatility_payloads
from tests.fixtures.volatility_series import build_volatility_series_scenario


def test_mock_writer_accepts_valid_rows_and_preserves_input() -> None:
    observation = build_volatility_observation(build_volatility_series_scenario("low_volatility"), "2026-01-15")
    rows = [observation]
    snapshot = deepcopy(rows)
    writer = VolatilityMockWriter()
    result = write_volatility_payloads(rows, writer=writer)
    assert result.accepted_count == 1
    assert result.rejected_count == 0
    assert rows == snapshot
    assert writer.rows


def test_mock_writer_rejects_invalid_rows() -> None:
    observation = build_volatility_observation(build_volatility_series_scenario("low_volatility"), "2026-01-15")
    observation = dict(observation)
    observation["volatility_regime_label"] = "NOT_ALLOWED"
    result = write_volatility_payloads([observation])
    assert result.accepted_count == 0
    assert result.rejected_count == 1
