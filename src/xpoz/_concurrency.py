from __future__ import annotations

import asyncio
from typing import TypeVar, Callable, Awaitable
from concurrent.futures import ThreadPoolExecutor

T = TypeVar("T")
R = TypeVar("R")

DEFAULT_CONCURRENCY = 10


def parallel_map(
    items: list[T],
    fn: Callable[[T], R],
    concurrency: int = DEFAULT_CONCURRENCY,
) -> list[R]:
    if not items:
        return []
    with ThreadPoolExecutor(max_workers=min(concurrency, len(items))) as pool:
        return list(pool.map(fn, items))


async def async_parallel_map(
    items: list[T],
    fn: Callable[[T], Awaitable[R]],
    concurrency: int = DEFAULT_CONCURRENCY,
) -> list[R]:
    if not items:
        return []
    semaphore = asyncio.Semaphore(concurrency)

    async def limited(item: T) -> R:
        async with semaphore:
            return await fn(item)

    return list(await asyncio.gather(*(limited(item) for item in items)))
