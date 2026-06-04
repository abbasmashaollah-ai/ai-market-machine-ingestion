from app.features.sector_rotation.sector_rotation_summary_engine import (
    build_sector_rotation_daily_summary,
    detect_deteriorating_rotation,
    detect_improving_rotation,
    determine_descriptive_rotation_state,
    get_top_bottom_symbols,
)


def test_top_bottom_symbols_are_deterministic_and_tie_broken_alphabetically() -> None:
    top, bottom = get_top_bottom_symbols({"XLK": 0.2, "XLF": 0.2, "XLP": 0.1, "XLE": -0.1}, top_n=2)
    assert top == ["XLF", "XLK"]
    assert bottom == ["XLE", "XLP"]


def test_improving_and_deteriorating_rotation_detection() -> None:
    improving_snapshot = {"XLK": {"rank_change_5d": 1, "rank_change_20d": 0, "deterioration_flag": False}}
    deteriorating_snapshot = {"XLK": {"rank_change_5d": -1, "rank_change_20d": 0, "deterioration_flag": True}}
    assert detect_improving_rotation(improving_snapshot) is True
    assert detect_deteriorating_rotation(deteriorating_snapshot) is True


def test_descriptive_state_evidence_labels() -> None:
    assert determine_descriptive_rotation_state(risk_on_leadership_score=0.8, defensive_leadership_score=0.2, broad_rotation_flag=True) == "RISK_ON_LEADERSHIP"
    assert determine_descriptive_rotation_state(risk_on_leadership_score=0.2, defensive_leadership_score=0.8, narrow_rotation_flag=True) == "DEFENSIVE_LEADERSHIP"
    assert determine_descriptive_rotation_state(broad_rotation_flag=True) == "BROAD_IMPROVEMENT"
    assert determine_descriptive_rotation_state(narrow_rotation_flag=True) == "NARROW_LEADERSHIP"
    assert determine_descriptive_rotation_state(deteriorating_rotation_flag=True, narrow_rotation_flag=True) == "BROAD_DETERIORATION"
    assert determine_descriptive_rotation_state() == "NO_CLEAR_ROTATION"


def test_daily_summary_includes_expected_fields_and_group_scores() -> None:
    summary = build_sector_rotation_daily_summary(
        {"XLK": 0.3, "XLF": 0.2, "XLP": 0.1, "XLE": -0.1, "XLV": 0.05}
    )

    assert set(summary) == {
        "risk_on_leadership_score",
        "cyclical_leadership_score",
        "defensive_leadership_score",
        "leadership_concentration_score",
        "sector_dispersion_score",
        "broad_rotation_flag",
        "narrow_rotation_flag",
        "improving_rotation_flag",
        "deteriorating_rotation_flag",
        "top_sector_symbols",
        "bottom_sector_symbols",
        "descriptive_rotation_state",
    }
    assert summary["risk_on_leadership_score"] is not None
    assert summary["cyclical_leadership_score"] is not None
    assert summary["defensive_leadership_score"] is not None
    assert isinstance(summary["top_sector_symbols"], list)
    assert isinstance(summary["bottom_sector_symbols"], list)
