from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from app.ingestion.manual.fred_macro_incremental import (
    ManualFREDMacroIncrementalPlan,
    build_manual_fred_macro_incremental_plan,
)
from app.state.manual_fred_macro import (
    ManualFREDMacroCheckpoint,
    ManualFREDMacroCheckpointStatus,
    build_manual_fred_macro_checkpoint,
)
from app.state.manual_fred_macro_results import (
    ManualFREDMacroRunResult,
    ManualFREDMacroRunStatus,
    build_manual_fred_macro_run_result,
)


@dataclass(frozen=True)
class ManualFREDMacroIncrementalPreview:
    plan: ManualFREDMacroIncrementalPlan
    checkpoints: tuple[ManualFREDMacroCheckpoint, ...]
    results: tuple[ManualFREDMacroRunResult, ...]
    metadata: dict[str, object] = field(default_factory=dict)


def build_manual_fred_macro_incremental_preview(
    *,
    plan_id: str,
    start_date: date,
    end_date: date,
    series_ids: tuple[str, ...] | None = None,
    category: str | None = None,
    include_all: bool = False,
) -> ManualFREDMacroIncrementalPreview:
    plan = build_manual_fred_macro_incremental_plan(
        plan_id=plan_id,
        start_date=start_date,
        end_date=end_date,
        series_ids=series_ids,
        category=category,
        include_all=include_all,
    )
    checkpoints: list[ManualFREDMacroCheckpoint] = []
    results: list[ManualFREDMacroRunResult] = []
    for job, run in zip(plan.jobs, plan.runs, strict=True):
        checkpoint = build_manual_fred_macro_checkpoint(
            checkpoint_key=job.job_id,
            vendor=job.vendor,
            dataset=job.dataset,
            series_id=job.metadata["series_id"],  # type: ignore[index]
            timeframe="1d",
            planned_start_date=start_date,
            planned_end_date=end_date,
            status=ManualFREDMacroCheckpointStatus.PLANNED,
        )
        checkpoints.append(checkpoint)
        results.append(
            build_manual_fred_macro_run_result(
                checkpoint_key=checkpoint.checkpoint_key,
                series_id=run.metadata["series_id"],  # type: ignore[index]
                status=ManualFREDMacroRunStatus.PLANNED,
                planned_start_date=start_date,
                planned_end_date=end_date,
                rows_planned=0,
                rows_fetched=0,
                rows_valid=0,
                rows_invalid=0,
                rows_written=0,
                validation_failures=0,
            )
        )

    return ManualFREDMacroIncrementalPreview(
        plan=plan,
        checkpoints=tuple(checkpoints),
        results=tuple(results),
        metadata={
            "manual_only": True,
            "series_count": len(plan.series_ids),
        },
    )
