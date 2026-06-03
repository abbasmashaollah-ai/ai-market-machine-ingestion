from app.features.breadth.breadth_engine import (
    calculate_advancers_decliners_unchanged,
    calculate_advancing_declining_volume,
    calculate_breadth_score,
    calculate_new_highs_lows,
    calculate_participation_score,
    calculate_percent_above_moving_average,
)


def test_advancers_decliners_unchanged_and_volume() -> None:
    previous = {"A": 10, "B": 10, "C": 10}
    latest = {"A": 11, "B": 9, "C": 10}
    volumes = {"A": 100, "B": 200, "C": 300}

    assert calculate_advancers_decliners_unchanged(previous, latest) == (1, 1, 1)
    assert calculate_advancing_declining_volume(previous, latest, volumes) == (100.0, 200.0)


def test_percent_above_moving_averages_and_new_highs_lows() -> None:
    histories = {
        "A": [{"close": value} for value in [1, 2, 3, 4, 5, 6]],
        "B": [{"close": value} for value in [6, 5, 4, 3, 2, 1]],
        "C": [{"close": value} for value in [2, 2, 2, 2, 2, 2]],
    }

    assert calculate_percent_above_moving_average(histories, 5) == 1 / 3
    assert calculate_new_highs_lows(histories, window=6) == (2, 2)


def test_scores() -> None:
    assert calculate_breadth_score(4, 2, 2) == 0.25
    assert calculate_participation_score(0.5, 0.75, 1.0) == 0.75
