from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time


@dataclass(frozen=True)
class DailyScheduleConfig:
    run_time: time
    timezone: str = "UTC"
    weekdays_only: bool = True
    metadata: dict[str, object] = field(default_factory=dict)
