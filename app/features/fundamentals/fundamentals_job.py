"""Dry-run orchestration for fundamentals observations."""

from __future__ import annotations

from dataclasses import dataclass

from .fundamentals_builder import build_fundamental_observation
from .fundamentals_report import build_fundamental_report
from .fundamentals_validator import validate_fundamental_observation, validate_fundamental_observations
from .fundamentals_writer import FundamentalsMockWriter, write_fundamental_payloads


@dataclass(frozen=True, slots=True)
class FundamentalsDryRunResult:
    observation_rows: tuple[dict[str, object], ...]
    reports: tuple[dict[str, object], ...]
    writer_result: object
    accepted_count: int
    rejected_count: int
    warnings: tuple[str, ...]
    no_db_writes: bool = True
    no_vendor_calls: bool = True
    no_scheduler_activation: bool = True


def run_fundamentals_dry_run(financials_by_symbol, observation_date, timestamp=None, writer=None):
    observations = [
        build_fundamental_observation(symbol, financials, observation_date, timestamp=timestamp)
        for symbol, financials in (financials_by_symbol or {}).items()
    ]
    validation = validate_fundamental_observations(observations)
    if not validation.is_valid:
        writer_result = write_fundamental_payloads([], writer=writer or FundamentalsMockWriter())
        return FundamentalsDryRunResult(
            observation_rows=tuple(observations),
            reports=tuple(build_fundamental_report(observation, writer_result=writer_result) for observation in observations),
            writer_result=writer_result,
            accepted_count=0,
            rejected_count=len(observations),
            warnings=tuple(str(error.message) for error in validation.errors),
        )
    writer_result = write_fundamental_payloads(observations, writer=writer)
    reports = tuple(build_fundamental_report(observation, writer_result=writer_result) for observation in observations)
    return FundamentalsDryRunResult(
        observation_rows=tuple(observations),
        reports=reports,
        writer_result=writer_result,
        accepted_count=writer_result.accepted_count,
        rejected_count=writer_result.rejected_count,
        warnings=tuple(),
    )
