from __future__ import annotations

from typing import Any, Awaitable, Callable, Generic, Iterator, TypeVar

T = TypeVar("T")


class CursorResult(Generic[T]):
    def __init__(
        self,
        data: list[T],
        has_more: bool,
        next_page_cursor: str | None,
        fetch_page: Callable[[str], CursorResult[T]],
    ):
        self.data = data
        self.has_more = has_more
        self.next_page_cursor = next_page_cursor
        self._fetch_page = fetch_page

    def has_next_page(self) -> bool:
        return self.has_more and self.next_page_cursor is not None

    def next_page(self) -> CursorResult[T]:
        if not self.has_next_page():
            raise IndexError("No more pages available")
        return self._fetch_page(self.next_page_cursor or "")

    def iter_pages(self) -> Iterator[CursorResult[T]]:
        page = self
        yield page
        while page.has_next_page():
            page = page.next_page()
            yield page

    def iter_items(self) -> Iterator[T]:
        for page in self.iter_pages():
            yield from page.data

    def __iter__(self) -> Iterator[T]:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        return f"CursorResult(items={len(self.data)}, has_more={self.has_more})"


class AsyncCursorResult(Generic[T]):
    def __init__(
        self,
        data: list[T],
        has_more: bool,
        next_page_cursor: str | None,
        fetch_page: Callable[[str], Awaitable[AsyncCursorResult[T]]],
    ):
        self.data = data
        self.has_more = has_more
        self.next_page_cursor = next_page_cursor
        self._fetch_page = fetch_page

    def has_next_page(self) -> bool:
        return self.has_more and self.next_page_cursor is not None

    async def next_page(self) -> AsyncCursorResult[T]:
        if not self.has_next_page():
            raise IndexError("No more pages available")
        return await self._fetch_page(self.next_page_cursor or "")

    async def iter_pages(self) -> Any:
        page = self
        yield page
        while page.has_next_page():
            page = await page.next_page()
            yield page

    async def iter_items(self) -> Any:
        async for page in self.iter_pages():
            for item in page.data:
                yield item

    def __iter__(self) -> Iterator[T]:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        return f"AsyncCursorResult(items={len(self.data)}, has_more={self.has_more})"
