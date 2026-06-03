import json

from app.features.breadth.breadth_builder import build_breadth_observation
from tests.fixtures.breadth_ohlcv import build_breadth_ohlcv_fixtures


def test_breadth_observation_includes_expected_fields() -> None:
    fixtures = build_breadth_ohlcv_fixtures()
    volume_histories = {symbol: [{"volume": row["volume"]} for row in history] for symbol, history in fixtures.items()}

    observation = build_breadth_observation("SP500", fixtures, volume_histories, "2026-01-15")

    expected_fields = {
        "universe",
        "observation_date",
        "timestamp",
        "advancers",
        "decliners",
        "unchanged",
        "advancing_volume",
        "declining_volume",
        "new_highs",
        "new_lows",
        "percent_above_20d",
        "percent_above_50d",
        "percent_above_200d",
        "breadth_score",
        "participation_score",
        "source",
        "quality_status",
        "certification_status",
        "freshness_status",
        "lineage",
        "evidence",
    }

    assert set(observation) == expected_fields
    assert observation["quality_status"] == "PENDING"
    json.dumps(observation)
