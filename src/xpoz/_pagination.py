from __future__ import annotations

from typing import TypeVar, Generic, Callable, Awaitable, Union

from xpoz.types.common import PaginationInfo
from xpoz._results import NoDataResult

T = TypeVar("T")


class PaginatedResult(Generic[T]):
    def __init__(
        self,
        data: list[T],
        pagination: PaginationInfo,
        table_name: str | None,
        export_operation_id: str | None,
        fetch_page: Callable[
            [int, str | None], Union["PaginatedResult[T]", NoDataResult]
        ],
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

    def next_page(self) -> Union[PaginatedResult[T], NoDataResult]:
        if not self.has_next_page():
            raise IndexError("No more pages available")
        return self._fetch_page_result(self.pagination.page_number + 1)

    def get_page(self, page_number: int) -> Union[PaginatedResult[T], NoDataResult]:
        if page_number < 1 or page_number > self.pagination.total_pages:
            raise ValueError(
                f"Page {page_number} out of range (1-{self.pagination.total_pages})"
            )
        return self._fetch_page_result(page_number)

    def export_csv(self) -> str:
        if self._fetch_export is None or self._export_operation_id is None:
            raise RuntimeError("CSV export not available for this result")
        return self._fetch_export(self._export_operation_id)

    def _fetch_page_result(
        self, page_number: int
    ) -> Union[PaginatedResult[T], NoDataResult]:
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
        fetch_page: Callable[
            [int, str | None],
            Awaitable[Union["AsyncPaginatedResult[T]", NoDataResult]],
        ],
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

    async def next_page(self) -> Union[AsyncPaginatedResult[T], NoDataResult]:
        if not self.has_next_page():
            raise IndexError("No more pages available")
        return await self._fetch_page_result(self.pagination.page_number + 1)

    async def get_page(
        self, page_number: int
    ) -> Union[AsyncPaginatedResult[T], NoDataResult]:
        if page_number < 1 or page_number > self.pagination.total_pages:
            raise ValueError(
                f"Page {page_number} out of range (1-{self.pagination.total_pages})"
            )
        return await self._fetch_page_result(page_number)

    async def export_csv(self) -> str:
        if self._fetch_export is None or self._export_operation_id is None:
            raise RuntimeError("CSV export not available for this result")
        return await self._fetch_export(self._export_operation_id)

    async def _fetch_page_result(
        self, page_number: int
    ) -> Union[AsyncPaginatedResult[T], NoDataResult]:
        return await self._fetch_page(page_number, self._table_name)

    def __repr__(self) -> str:
        return (
            f"AsyncPaginatedResult(items={len(self.data)}, "
            f"page={self.pagination.page_number}/{self.pagination.total_pages}, "
            f"total={self.pagination.total_rows})"
        )
