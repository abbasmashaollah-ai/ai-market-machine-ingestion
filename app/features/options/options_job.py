"""Dry-run orchestration for options observations."""

from __future__ import annotations

from dataclasses import dataclass

from .options_builder import build_options_observation
from .options_report import build_options_report
from .options_validator import validate_options_observation, validate_options_observations
from .options_writer import OptionsMockWriter, write_options_payloads


@dataclass(frozen=True, slots=True)
class OptionsDryRunResult:
    observation_rows: tuple[dict[str, object], ...]
    reports: tuple[dict[str, object], ...]
    writer_result: object
    accepted_count: int
    rejected_count: int
    warnings: tuple[str, ...]
    no_db_writes: bool = True
    no_vendor_calls: bool = True
    no_scheduler_activation: bool = True


def run_options_dry_run(input_payload, observation_date, timestamp=None, writer=None):
    observation = build_options_observation(
        input_payload.get("symbol", "UNKNOWN") if isinstance(input_payload, dict) else "UNKNOWN",
        input_payload,
        observation_date,
        timestamp=timestamp,
    )
    validation = validate_options_observation(observation)
    if not validation.is_valid:
        writer_result = write_options_payloads([], writer=writer or OptionsMockWriter())
        return OptionsDryRunResult(
            observation_rows=(observation,),
            reports=(build_options_report(observation, writer_result=writer_result),),
            writer_result=writer_result,
            accepted_count=0,
            rejected_count=1,
            warnings=tuple(str(error.message) for error in validation.errors),
        )
    writer_result = write_options_payloads([observation], writer=writer)
    report = build_options_report(observation, writer_result=writer_result)
    return OptionsDryRunResult(
        observation_rows=(observation,),
        reports=(report,),
        writer_result=writer_result,
        accepted_count=writer_result.accepted_count,
        rejected_count=writer_result.rejected_count,
        warnings=tuple(),
    )
