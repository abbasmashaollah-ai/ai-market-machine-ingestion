"""Dry-run orchestration for flows and positioning observations."""

from __future__ import annotations

from dataclasses import dataclass

from .flows_positioning_observation_builder import build_flows_positioning_observation
from .flows_positioning_report import build_flows_positioning_report
from .flows_positioning_validator import validate_flows_positioning_observation, validate_flows_positioning_observations
from .flows_positioning_writer import FlowsPositioningMockWriter, write_flows_positioning_payloads


@dataclass(frozen=True, slots=True)
class FlowsPositioningDryRunResult:
    observation_rows: tuple[dict[str, object], ...]
    reports: tuple[dict[str, object], ...]
    writer_result: object
    accepted_count: int
    rejected_count: int
    warnings: tuple[str, ...]
    no_db_writes: bool = True
    no_vendor_calls: bool = True
    no_scheduler_activation: bool = True


def run_flows_positioning_dry_run(input_payload, observation_date, timestamp=None, writer=None):
    observation = build_flows_positioning_observation(input_payload, observation_date, timestamp=timestamp)
    validation = validate_flows_positioning_observation(observation)
    if not validation.is_valid:
        writer_result = write_flows_positioning_payloads([], writer=writer or FlowsPositioningMockWriter())
        return FlowsPositioningDryRunResult(
            observation_rows=(observation,),
            reports=(build_flows_positioning_report(observation, writer_result=writer_result),),
            writer_result=writer_result,
            accepted_count=0,
            rejected_count=1,
            warnings=tuple(str(error.message) for error in validation.errors),
        )
    writer_result = write_flows_positioning_payloads([observation], writer=writer)
    report = build_flows_positioning_report(observation, writer_result=writer_result)
    return FlowsPositioningDryRunResult(
        observation_rows=(observation,),
        reports=(report,),
        writer_result=writer_result,
        accepted_count=writer_result.accepted_count,
        rejected_count=writer_result.rejected_count,
        warnings=tuple(),
    )
