from __future__ import annotations

from typing import TypeVar, Generic, Callable, Any, Awaitable

from xpoz.types.common import PaginationInfo

T = TypeVar("T")


class PaginatedResult(Generic[T]):
    def __init__(
        self,
        data: list[T],
        pagination: PaginationInfo,
        table_name: str | None,
        export_operation_id: str | None,
        fetch_page: Callable[[int, str | None], PaginatedResult[T]],
        fetch_export: Callable[[str], str] | None,
    ):
        self.data = data
        self.pagination = pagination
        self._table_name = table_name
        self._export_operation_id = export_operation_id
        self._fetch_page = fetch_page
        self._fetch_export = fetch_export

    def has_next_page(self) -> bool:
        return self.pagination.page_number < self.pagination.total_pages

    def next_page(self) -> PaginatedResult[T]:
        if not self.has_next_page():
            raise StopIteration("No more pages available")
        return self._fetch_page_result(self.pagination.page_number + 1)

    def get_page(self, page_number: int) -> PaginatedResult[T]:
        if page_number < 1 or page_number > self.pagination.total_pages:
            raise ValueError(
                f"Page {page_number} out of range (1-{self.pagination.total_pages})"
            )
        return self._fetch_page_result(page_number)

    def get_all_pages(self) -> list[T]:
        all_data = list(self.data)
        current_page = self.pagination.page_number
        while current_page < self.pagination.total_pages:
            current_page += 1
            result = self._fetch_page_result(current_page)
            all_data.extend(result.data)
        return all_data

    def export_csv(self) -> str:
        if self._fetch_export is None or self._export_operation_id is None:
            raise RuntimeError("CSV export not available for this result")
        return self._fetch_export(self._export_operation_id)

    def _fetch_page_result(self, page_number: int) -> PaginatedResult[T]:
        return self._fetch_page(page_number, self._table_name)

    def __repr__(self) -> str:
        return (
            f"PaginatedResult(items={len(self.data)}, "
            f"page={self.pagination.page_number}/{self.pagination.total_pages}, "
            f"total={self.pagination.total_rows})"
        )


class AsyncPaginatedResult(Generic[T]):
    def __init__(
        self,
        data: list[T],
        pagination: PaginationInfo,
        table_name: str | None,
        export_operation_id: str | None,
        fetch_page: Callable[[int, str | None], Awaitable[AsyncPaginatedResult[T]]],
        fetch_export: Callable[[str], Awaitable[str]] | None,
    ):
        self.data = data
        self.pagination = pagination
        self._table_name = table_name
        self._export_operation_id = export_operation_id
        self._fetch_page = fetch_page
        self._fetch_export = fetch_export

    def has_next_page(self) -> bool:
        return self.pagination.page_number < self.pagination.total_pages

    async def next_page(self) -> AsyncPaginatedResult[T]:
        if not self.has_next_page():
            raise StopIteration("No more pages available")
        return await self._fetch_page_result(self.pagination.page_number + 1)

    async def get_page(self, page_number: int) -> AsyncPaginatedResult[T]:
        if page_number < 1 or page_number > self.pagination.total_pages:
            raise ValueError(
                f"Page {page_number} out of range (1-{self.pagination.total_pages})"
            )
        return await self._fetch_page_result(page_number)

    async def get_all_pages(self) -> list[T]:
        all_data = list(self.data)
        current_page = self.pagination.page_number
        while current_page < self.pagination.total_pages:
            current_page += 1
            result = await self._fetch_page_result(current_page)
            all_data.extend(result.data)
        return all_data

    async def export_csv(self) -> str:
        if self._fetch_export is None or self._export_operation_id is None:
            raise RuntimeError("CSV export not available for this result")
        return await self._fetch_export(self._export_operation_id)

    async def _fetch_page_result(self, page_number: int) -> AsyncPaginatedResult[T]:
        return await self._fetch_page(page_number, self._table_name)

    def __repr__(self) -> str:
        return (
            f"AsyncPaginatedResult(items={len(self.data)}, "
            f"page={self.pagination.page_number}/{self.pagination.total_pages}, "
            f"total={self.pagination.total_rows})"
        )
