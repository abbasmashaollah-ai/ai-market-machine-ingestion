import json
from datetime import datetime, timezone

from app.features.breadth.breadth_builder import build_breadth_observation
from app.features.breadth.breadth_job import run_breadth_dry_run
from app.features.breadth.breadth_report import build_breadth_report
from tests.fixtures.breadth_ohlcv import build_breadth_fixture_histories_scenario


def _observation_for_scenario(scenario: str):
    close_histories, volume_histories = build_breadth_fixture_histories_scenario(scenario)
    return build_breadth_observation("SP500", close_histories, volume_histories, "2026-01-15")


def test_broad_strength_has_more_advancers_than_decliners() -> None:
    observation = _observation_for_scenario("broad_strength")
    assert observation["advancers"] > observation["decliners"]


def test_broad_weakness_has_more_decliners_than_advancers() -> None:
    observation = _observation_for_scenario("broad_weakness")
    assert observation["decliners"] > observation["advancers"]


def test_mixed_has_both_advancers_and_decliners() -> None:
    observation = _observation_for_scenario("mixed")
    assert observation["advancers"] > 0
    assert observation["decliners"] > 0


def test_narrow_strength_does_not_look_like_broad_participation() -> None:
    observation = _observation_for_scenario("narrow_strength")
    report = build_breadth_report(observation)
    assert report["participation_label"] != "BROAD_STRENGTH"
    assert report["participation_label"] != "BROAD_WEAKNESS"
    assert report["participation_score"] is not None


def test_reports_include_participation_metrics() -> None:
    observation = _observation_for_scenario("broad_strength")
    report = build_breadth_report(observation)
    assert report["participation_label"] in {
        "BROAD_STRENGTH",
        "BROAD_WEAKNESS",
        "MIXED_PARTICIPATION",
        "NARROW_PARTICIPATION",
        "INSUFFICIENT_DATA",
    }
    assert "advancer_decliner_ratio" in report
    assert "advancing_volume_share" in report
    assert "declining_volume_share" in report
    json.dumps(report)


def test_dry_run_works_for_all_scenarios() -> None:
    for scenario in ("broad_strength", "broad_weakness", "mixed", "narrow_strength"):
        close_histories, volume_histories = build_breadth_fixture_histories_scenario(scenario)
        result = run_breadth_dry_run(
            close_histories,
            volume_histories,
            universe="SP500",
            observation_date="2026-01-15",
            timestamp=datetime(2026, 1, 15, 16, 0, tzinfo=timezone.utc),
        )
        assert result.accepted_count == 1
        assert result.rejected_count == 0
        assert result.no_db_writes is True
        assert result.no_vendor_calls is True
        assert result.no_scheduler_activation is True
        assert result.reports
