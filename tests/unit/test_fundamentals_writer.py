from copy import deepcopy

from app.features.fundamentals.fundamentals_builder import build_fundamental_observation
from app.features.fundamentals.fundamentals_writer import FundamentalsMockWriter, write_fundamental_payloads
from tests.fixtures.fundamentals_data import build_fundamentals_financials_scenario


def test_mock_writer_accepts_valid_rows() -> None:
    observation = build_fundamental_observation("AAPL", build_fundamentals_financials_scenario("strong_quality")["AAPL"], "2026-01-15")
    writer = FundamentalsMockWriter()
    result = write_fundamental_payloads([observation], writer=writer)
    assert result.accepted_count == 1
    assert result.rejected_count == 0
    assert result.no_db_writes is True


def test_mock_writer_preserves_input() -> None:
    observation = build_fundamental_observation("AAPL", build_fundamentals_financials_scenario("strong_quality")["AAPL"], "2026-01-15")
    snapshot = deepcopy(observation)
    write_fundamental_payloads([observation], writer=FundamentalsMockWriter())
    assert observation == snapshot
