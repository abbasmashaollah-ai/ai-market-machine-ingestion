from __future__ import annotations


def build_logging_context(
    *,
    run_id: str | None = None,
    vendor: str | None = None,
    dataset: str | None = None,
    symbol: str | None = None,
    timeframe: str | None = None,
    job_id: str | None = None,
    status: str | None = None,
) -> dict[str, str]:
    context: dict[str, str] = {}
    if run_id is not None:
        context["run_id"] = run_id
    if vendor is not None:
        context["vendor"] = vendor
    if dataset is not None:
        context["dataset"] = dataset
    if symbol is not None:
        context["symbol"] = symbol
    if timeframe is not None:
        context["timeframe"] = timeframe
    if job_id is not None:
        context["job_id"] = job_id
    if status is not None:
        context["status"] = status
    return context

