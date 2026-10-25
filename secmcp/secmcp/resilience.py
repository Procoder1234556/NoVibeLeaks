"""Fault-tolerance helpers: retries with jitter, bulkheads (Day 14 / Day 5 series)."""

from __future__ import annotations

import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")

# Cap parallel live provider checks — avoids self-inflicted rate-limit spikes (batch scans).
MAX_VALIDATION_CONCURRENCY = 3

# Retry transient provider/network failures only (not 401/invalid).
VALIDATION_MAX_ATTEMPTS = 3
VALIDATION_RETRY_BASE_SEC = 0.25

_validation_semaphore: asyncio.Semaphore | None = None


def validation_semaphore() -> asyncio.Semaphore:
    global _validation_semaphore
    if _validation_semaphore is None:
        _validation_semaphore = asyncio.Semaphore(MAX_VALIDATION_CONCURRENCY)
    return _validation_semaphore


def retry_delay_seconds(attempt: int) -> float:
    """Exponential backoff with full jitter (AWS-style). attempt is 1-based."""
    cap = VALIDATION_RETRY_BASE_SEC * (2 ** (attempt - 1))
    return random.uniform(0, cap)


async def with_validation_bulkhead(coro: Awaitable[T]) -> T:
    async with validation_semaphore():
        return await coro


async def retry_transient(
    operation: Callable[[], Awaitable[T]],
    *,
    is_transient: Callable[[T], bool],
    max_attempts: int = VALIDATION_MAX_ATTEMPTS,
) -> T:
    last: T | None = None
    for attempt in range(1, max_attempts + 1):
        last = await operation()
        if not is_transient(last) or attempt >= max_attempts:
            return last
        await asyncio.sleep(retry_delay_seconds(attempt))
    assert last is not None
    return last
