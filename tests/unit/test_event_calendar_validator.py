from copy import deepcopy

from app.features.event_calendar.event_calendar_builder import build_event_calendar_observation
from app.features.event_calendar.event_calendar_validator import validate_event_calendar_observation, validate_event_calendar_observations
from tests.fixtures.event_calendar_events import build_event_calendar_events_scenario


def test_valid_observation_passes() -> None:
    observation = build_event_calendar_observation(build_event_calendar_events_scenario("quiet_week"), "2026-06-03")
    result = validate_event_calendar_observation(observation)
    assert result.is_valid is True


def test_invalid_rows_fail_and_input_not_mutated() -> None:
    observation = build_event_calendar_observation(build_event_calendar_events_scenario("quiet_week"), "2026-06-03")
    snapshot = deepcopy(observation)
    observation["lookahead_days"] = 0
    result = validate_event_calendar_observation(observation)
    assert result.is_valid is False
    assert any(error.field_name == "lookahead_days" for error in result.errors)
    assert snapshot["lookahead_days"] == 10


def test_duplicate_keys_fail() -> None:
    observation = build_event_calendar_observation(build_event_calendar_events_scenario("quiet_week"), "2026-06-03")
    result = validate_event_calendar_observations([observation, dict(observation)])
    assert result.is_valid is False
