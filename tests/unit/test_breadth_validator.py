from app.features.breadth.breadth_builder import build_breadth_observation
from app.features.breadth.breadth_validator import validate_breadth_observation, validate_breadth_observations
from tests.fixtures.breadth_ohlcv import build_breadth_ohlcv_fixtures


def _observation():
    fixtures = build_breadth_ohlcv_fixtures()
    volume_histories = {symbol: [{"volume": row["volume"]} for row in history] for symbol, history in fixtures.items()}
    return build_breadth_observation("SP500", fixtures, volume_histories, "2026-01-15")


def test_valid_observation_passes() -> None:
    result = validate_breadth_observation(_observation())
    assert result.is_valid is True


def test_invalid_rows_fail() -> None:
    row = dict(_observation())
    row.pop("universe")
    row["advancers"] = -1
    row["breadth_score"] = "bad"
    result = validate_breadth_observation(row)
    assert result.is_valid is False


def test_duplicate_batch_key_fails() -> None:
    rows = [_observation(), _observation()]
    results = validate_breadth_observations(rows)
    assert results[0].is_valid is True
    assert results[1].is_valid is False
