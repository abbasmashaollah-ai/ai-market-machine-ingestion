from __future__ import annotations

from app.vendors.common.throttling import DeterministicRateLimiter, RateLimitExceededError


class PolygonRateLimiter:
    def __init__(self, requests_per_minute: int) -> None:
        self._limiter = DeterministicRateLimiter(requests_per_minute)

    def allow(self, now: float | None = None) -> bool:
        return self._limiter.allow(now=now)

    def acquire(self, now: float | None = None) -> None:
        self._limiter.acquire(now=now)


__all__ = ["PolygonRateLimiter", "RateLimitExceededError"]
