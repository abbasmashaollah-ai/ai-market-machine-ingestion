from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from uuid import uuid4


def generate_run_id() -> str:
    return uuid4().hex


def get_environment() -> str:
    from app.core.config import load_settings

    return load_settings().ENVIRONMENT


@dataclass(frozen=True)
class RuntimeContext:
    run_id: str
    environment: str
    vendor: str | None = None
    dataset: str | None = None
    symbol: str | None = None
    timeframe: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


def build_runtime_context(
    *,
    run_id: str | None = None,
    environment: str | None = None,
    vendor: str | None = None,
    dataset: str | None = None,
    symbol: str | None = None,
    timeframe: str | None = None,
) -> RuntimeContext:
    from app.core.config import load_settings

    settings = load_settings()
    return RuntimeContext(
        run_id=run_id or generate_run_id(),
        environment=environment or settings.ENVIRONMENT,
        vendor=vendor,
        dataset=dataset,
        symbol=symbol,
        timeframe=timeframe,
    )


def with_context(
    context: RuntimeContext,
    **updates: str | None,
) -> RuntimeContext:
    return replace(context, **updates)
