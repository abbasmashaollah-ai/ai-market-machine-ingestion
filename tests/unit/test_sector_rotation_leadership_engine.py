import pytest

from app.features.sector_rotation.sector_leadership_engine import (
    build_rank_map,
    build_sector_leadership_snapshot,
    calculate_momentum_score,
    calculate_rank_change,
    calculate_rank_changes,
    is_deteriorating,
    is_leadership_rank,
)


def test_build_rank_map_strongest_gets_rank_one() -> None:
    ranks = build_rank_map({"XLK": 0.15, "XLF": 0.10, "XLP": 0.05})
    assert ranks == {"XLK": 1, "XLF": 2, "XLP": 3}


def test_build_rank_map_uses_alphabetical_tie_break() -> None:
    ranks = build_rank_map({"XLF": 0.10, "XLK": 0.10, "XLP": 0.05})
    assert ranks == {"XLF": 1, "XLK": 2, "XLP": 3}


def test_rank_change_sign_convention() -> None:
    assert calculate_rank_change(5, 3) == 2
    assert calculate_rank_change(3, 5) == -2
    assert calculate_rank_change(None, 5) is None


def test_calculate_rank_changes_is_deterministic() -> None:
    changes = calculate_rank_changes({"XLK": 4, "XLF": 2}, {"XLK": 2, "XLF": 3, "XLP": 1})
    assert changes == {"XLF": -1, "XLK": 2, "XLP": None}


def test_leadership_flag_top_n_behavior() -> None:
    assert is_leadership_rank(1)
    assert is_leadership_rank(3)
    assert is_leadership_rank(4) is False
    assert is_leadership_rank(None) is False


def test_deterioration_flag_on_worsening_rank_or_weakening_strength() -> None:
    assert is_deteriorating(rank_change_5d=-1) is True
    assert is_deteriorating(rank_change_5d=1, rank_change_20d=0, relative_strength_5d=0.01, relative_strength_20d=0.02) is True
    assert is_deteriorating(rank_change_5d=1, rank_change_20d=1, relative_strength_5d=0.05, relative_strength_20d=0.01) is False


def test_momentum_score_is_deterministic_and_bounded() -> None:
    score = calculate_momentum_score(
        relative_strength_5d=0.08,
        relative_strength_20d=0.10,
        relative_strength_60d=0.12,
        rank_change_5d=2,
        rank_change_20d=1,
    )
    assert score is not None
    assert -1.0 <= score <= 1.0
    assert score == calculate_momentum_score(
        relative_strength_5d=0.08,
        relative_strength_20d=0.10,
        relative_strength_60d=0.12,
        rank_change_5d=2,
        rank_change_20d=1,
    )


def test_snapshot_output_includes_expected_fields_and_none_fallback() -> None:
    snapshot = build_sector_leadership_snapshot(
        {
            "5d": {"XLK": 0.08, "XLF": 0.06, "XLP": 0.02},
            "20d": {"XLK": 0.07, "XLF": 0.05, "XLP": 0.03},
            "60d": {"XLK": 0.06, "XLF": 0.04, "XLP": 0.01},
        }
    )

    assert set(snapshot) == {"XLK", "XLF", "XLP"}
    xlk = snapshot["XLK"]
    assert set(xlk) == {
        "rank_5d",
        "rank_20d",
        "rank_60d",
        "rank_change_5d",
        "rank_change_20d",
        "momentum_score",
        "leadership_flag",
        "deterioration_flag",
    }
    assert xlk["leadership_flag"] is True
    assert xlk["deterioration_flag"] is False
    assert xlk["rank_change_5d"] is None or isinstance(xlk["rank_change_5d"], int)


def test_none_inputs_do_not_crash() -> None:
    snapshot = build_sector_leadership_snapshot({"5d": {"XLK": None}, "20d": {"XLK": None}})
    assert snapshot["XLK"]["rank_5d"] is None
    assert snapshot["XLK"]["momentum_score"] is None
