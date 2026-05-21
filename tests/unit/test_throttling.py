import unittest

from app.vendors.common.throttling import DeterministicRateLimiter, RateLimitExceededError


class ThrottlingTests(unittest.TestCase):
    def test_rate_limiter_allows_within_limit(self) -> None:
        limiter = DeterministicRateLimiter(2)
        self.assertTrue(limiter.allow(now=0))
        self.assertTrue(limiter.allow(now=1))
        self.assertFalse(limiter.allow(now=2))

    def test_rate_limiter_resets_after_window(self) -> None:
        limiter = DeterministicRateLimiter(1)
        self.assertTrue(limiter.allow(now=0))
        self.assertTrue(limiter.allow(now=61))

    def test_acquire_raises_when_exceeded(self) -> None:
        limiter = DeterministicRateLimiter(1)
        limiter.acquire(now=0)
        with self.assertRaises(RateLimitExceededError):
            limiter.acquire(now=1)
