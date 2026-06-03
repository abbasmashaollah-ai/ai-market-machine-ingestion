from app.features.sector_rotation.sector_dispersion_engine import (
    calculate_breadth_of_positive_scores,
    calculate_leadership_concentration_score,
    calculate_sector_dispersion_score,
    detect_broad_rotation,
    detect_narrow_rotation,
)


def test_dispersion_returns_none_for_empty_or_invalid_values() -> None:
    assert calculate_sector_dispersion_score({}) is None
    assert calculate_sector_dispersion_score({"XLK": None, "XLF": None}) is None


def test_dispersion_is_deterministic_for_valid_scores() -> None:
    score = calculate_sector_dispersion_score({"XLK": 0.1, "XLF": 0.2, "XLP": 0.3})
    assert score is not None
    assert score == calculate_sector_dispersion_score({"XLP": 0.3, "XLF": 0.2, "XLK": 0.1})


def test_concentration_detects_concentrated_leadership() -> None:
    concentrated = calculate_leadership_concentration_score({"XLK": 0.9, "XLF": 0.05, "XLP": 0.05}, top_n=1)
    dispersed = calculate_leadership_concentration_score({"XLK": 0.4, "XLF": 0.3, "XLP": 0.3}, top_n=1)
    assert concentrated is not None and dispersed is not None
    assert concentrated > dispersed


def test_positive_breadth_ratio_and_flags() -> None:
    scores = {"XLK": 0.2, "XLF": 0.1, "XLP": -0.05, "XLE": 0.15, "XLI": 0.05}
    breadth = calculate_breadth_of_positive_scores(scores)
    assert breadth == 4 / 5
    assert detect_broad_rotation(scores, min_positive_ratio=0.6) is True
    assert detect_narrow_rotation({"XLK": 0.9, "XLF": 0.05, "XLP": 0.05}, concentration_threshold=0.5) is True


def test_no_valid_group_returns_none() -> None:
    assert calculate_leadership_concentration_score({"XLK": None, "XLF": None}) is None
    assert calculate_breadth_of_positive_scores({"XLK": None}) is None

