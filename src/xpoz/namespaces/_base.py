from __future__ import annotations

from typing import TypeVar, Any, Callable, Awaitable, Type

from pydantic import BaseModel

from xpoz._field_mapping import map_fields_to_camel, map_dict_keys_to_snake
from xpoz._polling import wait_for_result, wait_for_result_sync
from xpoz._pagination import PaginatedResult, AsyncPaginatedResult
from xpoz.types.common import PaginationInfo

T = TypeVar("T", bound=BaseModel)


def _parse_item(model: Type[T], raw: dict[str, Any]) -> T:
    return model.model_validate(map_dict_keys_to_snake(raw))


def _parse_items(model: Type[T], raw_list: list[dict[str, Any]]) -> list[T]:
    return [_parse_item(model, item) for item in raw_list]


def _extract_pagination(raw: dict[str, Any]) -> PaginationInfo:
    pag: dict[str, Any] = raw.get("pagination", {})
    return PaginationInfo(
        table_name=pag.get("tableName"),
        total_rows=pag.get("totalRows", 0),
        total_pages=pag.get("totalPages", 0),
        page_number=pag.get("pageNumber", 1),
        page_size=pag.get("pageSize", 100),
        results_count=pag.get("resultsCount", 0),
    )


def _extract_results(raw: dict[str, Any]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = raw.get("results", [])
    return results


def _extract_export_op_id(raw: dict[str, Any]) -> str | None:
    val: str | None = raw.get("dataDumpExportOperationId")
    return val


class BaseNamespace:
    def __init__(self, call_tool: Callable[[str, dict[str, Any]], dict[str, Any]], timeout: float):
        self._call_tool = call_tool
        self._timeout = timeout

    def _call_and_maybe_poll(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        result = self._call_tool(tool_name, arguments)
        operation_id = result.get("operationId")
        if operation_id:
            return wait_for_result_sync(self._call_tool, operation_id, self._timeout)
        return result

    def _build_paginated_result(
        self,
        raw: dict[str, Any],
        model: Type[T],
        tool_name: str,
        base_args: dict[str, Any],
    ) -> PaginatedResult[T]:
        items = _parse_items(model, _extract_results(raw))
        pagination = _extract_pagination(raw)
        table_name = pagination.table_name
        export_op_id = _extract_export_op_id(raw)

        def fetch_page(page_number: int, tbl: str | None) -> PaginatedResult[T]:
            args = {**base_args, "pageNumber": page_number}
            if tbl:
                args["tableName"] = tbl
            page_raw = self._call_and_maybe_poll(tool_name, args)
            return self._build_paginated_result(page_raw, model, tool_name, base_args)

        def fetch_export(op_id: str) -> str:
            poll_result = wait_for_result_sync(self._call_tool, op_id, self._timeout)
            url: str = poll_result.get("downloadUrl", "")
            return url

        return PaginatedResult(
            data=items,
            pagination=pagination,
            table_name=table_name,
            export_operation_id=export_op_id,
            fetch_page=fetch_page,
            fetch_export=fetch_export,
        )

    def _build_args(self, **kwargs: Any) -> dict[str, Any]:
        args: dict[str, Any] = {}
        for key, value in kwargs.items():
            if value is not None:
                args[key] = value
        return args

    def _convert_fields(self, fields: list[str] | None) -> list[str] | None:
        return map_fields_to_camel(fields)


class AsyncBaseNamespace:
    def __init__(
        self,
        call_tool: Callable[[str, dict[str, Any]], Awaitable[dict[str, Any]]],
        timeout: float,
    ):
        self._call_tool = call_tool
        self._timeout = timeout

    async def _call_and_maybe_poll(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        result = await self._call_tool(tool_name, arguments)
        operation_id = result.get("operationId")
        if operation_id:
            return await wait_for_result(self._call_tool, operation_id, self._timeout)
        return result

    async def _build_paginated_result(
        self,
        raw: dict[str, Any],
        model: Type[T],
        tool_name: str,
        base_args: dict[str, Any],
    ) -> AsyncPaginatedResult[T]:
        items = _parse_items(model, _extract_results(raw))
        pagination = _extract_pagination(raw)
        table_name = pagination.table_name
        export_op_id = _extract_export_op_id(raw)

        async def fetch_page(
            page_number: int, tbl: str | None
        ) -> AsyncPaginatedResult[T]:
            args = {**base_args, "pageNumber": page_number}
            if tbl:
                args["tableName"] = tbl
            page_raw = await self._call_and_maybe_poll(tool_name, args)
            return await self._build_paginated_result(page_raw, model, tool_name, base_args)

        async def fetch_export(op_id: str) -> str:
            poll_result = await wait_for_result(self._call_tool, op_id, self._timeout)
            url: str = poll_result.get("downloadUrl", "")
            return url

        return AsyncPaginatedResult(
            data=items,
            pagination=pagination,
            table_name=table_name,
            export_operation_id=export_op_id,
            fetch_page=fetch_page,
            fetch_export=fetch_export,
        )

    def _build_args(self, **kwargs: Any) -> dict[str, Any]:
        args: dict[str, Any] = {}
        for key, value in kwargs.items():
            if value is not None:
                args[key] = value
        return args

    def _convert_fields(self, fields: list[str] | None) -> list[str] | None:
        return map_fields_to_camel(fields)
