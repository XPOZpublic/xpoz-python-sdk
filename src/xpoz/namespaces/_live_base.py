from __future__ import annotations

from typing import Any, Type, TypeVar

from pydantic import BaseModel

from xpoz._cursor import AsyncCursorResult, CursorResult
from xpoz._rest import AsyncRestTransport, RestTransport
from xpoz._transform._field_mapping import map_dict_keys_to_snake, map_fields_to_camel

T = TypeVar("T", bound=BaseModel)

CONNECTION_FOLLOWERS = "followers"
CONNECTION_FOLLOWING = "following"

_STRING_ID_FIELDS = ("id", "user_id", "post_id", "author_id")


def _csv_fields(fields: list[str] | None) -> str | None:
    converted = map_fields_to_camel(fields)
    if not converted:
        return None
    return ",".join(converted)


def _coerce_string_ids(item: dict[str, Any]) -> dict[str, Any]:
    for field in _STRING_ID_FIELDS:
        value = item.get(field)
        if isinstance(value, int):
            item[field] = str(value)
    return item


def _parse_items(model: Type[T], raw_list: list[dict[str, Any]]) -> list[T]:
    return [
        model.model_validate(_coerce_string_ids(map_dict_keys_to_snake(item)))
        for item in raw_list
    ]


class LiveNamespace:
    def __init__(self, transport: RestTransport):
        self._transport = transport

    def _page(
        self,
        model: Type[T],
        path: str,
        params: dict[str, Any],
    ) -> CursorResult[T]:
        payload = self._transport.get(path, params)

        def fetch_page(cursor: str) -> CursorResult[T]:
            return self._page(model, path, {**params, "cursor": cursor})

        return CursorResult(
            data=_parse_items(model, payload.get("results", [])),
            has_more=bool(payload.get("has_more")),
            next_page_cursor=payload.get("next_page_cursor"),
            fetch_page=fetch_page,
        )

    def _single(self, model: Type[T], path: str, params: dict[str, Any]) -> T | None:
        page = self._page(model, path, params)
        return page.data[0] if page.data else None


class AsyncLiveNamespace:
    def __init__(self, transport: AsyncRestTransport):
        self._transport = transport

    async def _page(
        self,
        model: Type[T],
        path: str,
        params: dict[str, Any],
    ) -> AsyncCursorResult[T]:
        payload = await self._transport.get(path, params)

        async def fetch_page(cursor: str) -> AsyncCursorResult[T]:
            return await self._page(model, path, {**params, "cursor": cursor})

        return AsyncCursorResult(
            data=_parse_items(model, payload.get("results", [])),
            has_more=bool(payload.get("has_more")),
            next_page_cursor=payload.get("next_page_cursor"),
            fetch_page=fetch_page,
        )

    async def _single(self, model: Type[T], path: str, params: dict[str, Any]) -> T | None:
        page = await self._page(model, path, params)
        return page.data[0] if page.data else None
