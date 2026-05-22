from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from app.ingestion.backfill.checkpoints import build_checkpoint_key
from app.ingestion.backfill.planner import BackfillRequest
from app.ingestion.pipelines.fred_macro import FredMacroPipelineRequest, plan_fred_macro_fetch_tasks
from app.state.jobs import IngestionJob, JobStatus
from app.state.runs import IngestionRun, RunStatus
from app.vendors.fred.series_catalog import SeriesCategory, get_active_series, get_series_by_category


@dataclass(frozen=True)
class ManualFREDMacroIncrementalPlan:
    plan_id: str
    vendor: str
    dataset: str
    start_date: date
    end_date: date
    series_ids: tuple[str, ...]
    jobs: tuple[IngestionJob, ...]
    runs: tuple[IngestionRun, ...]
    checkpoint_keys: tuple[str, ...]
    fetch_tasks: tuple[object, ...]
    metadata: dict[str, object] = field(default_factory=dict)


def select_incremental_series_ids(
    *,
    series_ids: tuple[str, ...] | None = None,
    category: str | None = None,
    include_all: bool = False,
) -> tuple[str, ...]:
    if series_ids:
        return tuple(series_ids)
    series = get_active_series()
    if category is not None:
        series = get_series_by_category(SeriesCategory(category))
    if include_all:
        return tuple(item.series_id for item in series)
    return tuple(item.series_id for item in series if item.priority == 1)


def build_manual_fred_macro_incremental_plan(
    *,
    plan_id: str,
    start_date: date,
    end_date: date,
    series_ids: tuple[str, ...] | None = None,
    category: str | None = None,
    include_all: bool = False,
) -> ManualFREDMacroIncrementalPlan:
    selected_series_ids = select_incremental_series_ids(
        series_ids=series_ids,
        category=category,
        include_all=include_all,
    )
    request = FredMacroPipelineRequest(
        series_ids=selected_series_ids,
        start_date=start_date,
        end_date=end_date,
        category=category,
        dry_run=True,
    )
    fetch_tasks = plan_fred_macro_fetch_tasks(request)
    jobs: list[IngestionJob] = []
    runs: list[IngestionRun] = []
    checkpoint_keys: list[str] = []

    for task in fetch_tasks:
        job_id = build_checkpoint_key(
            vendor=task.vendor,
            dataset=task.dataset,
            symbol=task.series_id,
            timeframe="1d",
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
        )
        jobs.append(
            IngestionJob(
                job_id=job_id,
                vendor=task.vendor,
                dataset=task.dataset,
                status=JobStatus.PENDING,
                metadata={
                    "series_id": task.series_id,
                    "category": task.category,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "manual_only": True,
                },
            )
        )
        runs.append(
            IngestionRun(
                run_id=job_id,
                job_id=job_id,
                status=RunStatus.PENDING,
                rows_fetched=0,
                rows_written=0,
                rows_rejected=0,
                error_count=0,
                metadata={
                    "series_id": task.series_id,
                    "category": task.category,
                    "manual_only": True,
                },
            )
        )
        checkpoint_keys.append(job_id)

    return ManualFREDMacroIncrementalPlan(
        plan_id=plan_id,
        vendor="fred",
        dataset="macro_observations",
        start_date=start_date,
        end_date=end_date,
        series_ids=selected_series_ids,
        jobs=tuple(jobs),
        runs=tuple(runs),
        checkpoint_keys=tuple(checkpoint_keys),
        fetch_tasks=fetch_tasks,
        metadata={
            "manual_only": True,
            "category": category,
            "include_all": include_all,
        },
    )


def describe_manual_plan(plan: ManualFREDMacroIncrementalPlan) -> dict[str, object]:
    return {
        "plan_id": plan.plan_id,
        "vendor": plan.vendor,
        "dataset": plan.dataset,
        "start_date": plan.start_date.isoformat(),
        "end_date": plan.end_date.isoformat(),
        "series_ids": plan.series_ids,
        "checkpoint_keys": plan.checkpoint_keys,
        "job_count": len(plan.jobs),
        "run_count": len(plan.runs),
        "manual_only": plan.metadata.get("manual_only", True),
    }
