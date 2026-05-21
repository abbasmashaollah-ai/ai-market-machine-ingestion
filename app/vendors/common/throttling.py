from __future__ import annotations

from dataclasses import dataclass
from time import monotonic


@dataclass(frozen=True)
class RateLimitState:
    requests_per_minute: int
    window_start: float
    request_count: int


class RateLimitExceededError(RuntimeError):
    pass


class DeterministicRateLimiter:
    def __init__(self, requests_per_minute: int) -> None:
        if requests_per_minute <= 0:
            raise ValueError("requests_per_minute must be positive")
        self._requests_per_minute = requests_per_minute
        self._window_start = 0.0
        self._request_count = 0
        self._initialized = False

    @property
    def state(self) -> RateLimitState:
        return RateLimitState(
            requests_per_minute=self._requests_per_minute,
            window_start=self._window_start,
            request_count=self._request_count,
        )

    def allow(self, now: float | None = None) -> bool:
        current = monotonic() if now is None else now
        if not self._initialized:
            self._window_start = current
            self._initialized = True
        if current - self._window_start >= 60:
            self._window_start = current
            self._request_count = 0
        if self._request_count >= self._requests_per_minute:
            return False
        self._request_count += 1
        return True

    def acquire(self, now: float | None = None) -> None:
        if not self.allow(now=now):
            raise RateLimitExceededError("rate limit exceeded")
