from copy import deepcopy

from app.features.prices.price_feature_builder import build_price_feature_observation
from app.features.prices.price_feature_writer import PriceFeatureMockWriter, write_price_feature_payloads
from tests.fixtures.price_ohlcv import build_price_ohlcv_fixtures


def test_mock_writer_accepts_valid_rows() -> None:
    fixtures = build_price_ohlcv_fixtures()
    rows = [
        build_price_feature_observation(symbol, [row["close"] for row in history], "2026-01-15")
        for symbol, history in fixtures.items()
    ]
    writer = PriceFeatureMockWriter()

    result = write_price_feature_payloads(rows, writer=writer)

    assert result.accepted_count == 3
    assert result.rejected_count == 0
    assert result.no_db_writes is True
    assert result.no_vendor_calls is True
    assert result.no_scheduler_activation is True
    assert len(writer.accepted_rows) == 3


def test_mock_writer_rejects_invalid_rows() -> None:
    fixtures = build_price_ohlcv_fixtures()
    valid = build_price_feature_observation("SPY", [row["close"] for row in fixtures["SPY"]], "2026-01-15")
    invalid = dict(valid)
    invalid["latest_close"] = 0
    writer = PriceFeatureMockWriter()

    result = write_price_feature_payloads([valid, invalid], writer=writer)

    assert result.accepted_count == 1
    assert result.rejected_count == 1
    assert result.errors


def test_input_rows_are_not_mutated() -> None:
    fixtures = build_price_ohlcv_fixtures()
    row = build_price_feature_observation("AAPL", [r["close"] for r in fixtures["AAPL"]], "2026-01-15")
    row_copy = deepcopy(row)
    writer = PriceFeatureMockWriter()

    write_price_feature_payloads([row], writer=writer)

    assert row == row_copy