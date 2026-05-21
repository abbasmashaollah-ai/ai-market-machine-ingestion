from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    backoff_seconds: float = 1.0
    max_backoff_seconds: float = 30.0
    jitter: bool = False


def build_retry_policy(
    *,
    max_attempts: int = 3,
    backoff_seconds: float = 1.0,
    max_backoff_seconds: float = 30.0,
    jitter: bool = False,
) -> RetryPolicy:
    return RetryPolicy(
        max_attempts=max_attempts,
        backoff_seconds=backoff_seconds,
        max_backoff_seconds=max_backoff_seconds,
        jitter=jitter,
    )
