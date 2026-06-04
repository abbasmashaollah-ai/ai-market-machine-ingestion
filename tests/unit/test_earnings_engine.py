from __future__ import annotations

from app.features.earnings.earnings_engine import (
    calculate_days_since_earnings,
    calculate_days_to_earnings,
    calculate_earnings_quality_score,
    calculate_earnings_risk_score,
    calculate_estimate_revision_score,
    calculate_guidance_score,
    calculate_implied_vs_actual_move_score,
    calculate_post_earnings_reaction_score,
    calculate_pre_earnings_drift_score,
    calculate_surprise_score,
    determine_earnings_regime_label,
)


def test_days_to_and_since_earnings() -> None:
    assert calculate_days_to_earnings("2026-07-01", "2026-07-10") == 9
    assert calculate_days_since_earnings("2026-07-15", "2026-07-10") == 5


def test_surprise_score_behavior() -> None:
    assert calculate_surprise_score(110, 100) == 0.1
    assert calculate_surprise_score(90, 100) == -0.1


def test_guidance_score() -> None:
    assert calculate_guidance_score("raise") == 1.0
    assert calculate_guidance_score("lower") == -1.0
    assert calculate_guidance_score("mixed") == 0.0


def test_estimate_revision_score() -> None:
    assert calculate_estimate_revision_score("positive") == 1.0
    assert calculate_estimate_revision_score("negative") == -1.0


def test_earnings_reaction_scores() -> None:
    assert calculate_pre_earnings_drift_score(5.0) == 0.5
    assert calculate_post_earnings_reaction_score(4.0, 6.0) == 0.35
    assert calculate_implied_vs_actual_move_score(4.0, 5.0) == 0.25


def test_earnings_quality_and_risk_scores() -> None:
    component_scores = {
        "eps_surprise_score": 0.5,
        "revenue_surprise_score": 0.25,
        "guidance_score": 1.0,
        "estimate_revision_score": 0.5,
    }
    quality = calculate_earnings_quality_score(component_scores)
    risk = calculate_earnings_risk_score(component_scores, days_to_earnings=10)
    assert quality is not None
    assert risk is not None
    assert 0.0 <= risk <= 1.0


def test_earnings_regime_labels() -> None:
    assert determine_earnings_regime_label({}, days_to_earnings=5) == "UPCOMING_EARNINGS_RISK"
    assert determine_earnings_regime_label({"post_earnings_reaction_score": 0.4}, days_since_earnings=1) == "POSITIVE_EARNINGS_REACTION"
    assert determine_earnings_regime_label({"post_earnings_reaction_score": -0.4}, days_since_earnings=1) == "NEGATIVE_EARNINGS_REACTION"

