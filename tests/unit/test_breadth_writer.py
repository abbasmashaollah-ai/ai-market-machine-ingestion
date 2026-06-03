from copy import deepcopy

from app.features.breadth.breadth_builder import build_breadth_observation
from app.features.breadth.breadth_writer import BreadthMockWriter, write_breadth_payloads
from tests.fixtures.breadth_ohlcv import build_breadth_ohlcv_fixtures


def _observation():
    fixtures = build_breadth_ohlcv_fixtures()
    volume_histories = {symbol: [{"volume": row["volume"]} for row in history] for symbol, history in fixtures.items()}
    return build_breadth_observation("SP500", fixtures, volume_histories, "2026-01-15")


def test_writer_accepts_valid_rows() -> None:
    writer = BreadthMockWriter()
    result = write_breadth_payloads([_observation()], writer=writer)
    assert result.accepted_count == 1
    assert result.rejected_count == 0
    assert result.no_db_writes is True
    assert len(writer.accepted_rows) == 1


def test_writer_rejects_invalid_rows_and_does_not_mutate_inputs() -> None:
    row = _observation()
    row_copy = deepcopy(row)
    invalid = dict(row)
    invalid["advancers"] = -1
    writer = BreadthMockWriter()
    result = write_breadth_payloads([row, invalid], writer=writer)
    assert result.accepted_count == 1
    assert result.rejected_count == 1
    assert row == row_copy
