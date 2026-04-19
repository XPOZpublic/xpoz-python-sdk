from __future__ import annotations

from typing import Any

from xpoz.namespaces._base import BaseNamespace, AsyncBaseNamespace, _parse_item, _parse_items
from xpoz._transform._field_mapping import map_dict_keys_to_snake
from xpoz.types.tracking import TrackedItem, AddTrackedItemsResult, RemoveTrackedItemsResult
from xpoz._config import _tools


class TrackingNamespace(BaseNamespace):
    def get_tracked_items(self) -> list[TrackedItem]:
        result = self._call_tool(_tools.GET_TRACKED_ITEMS, {})
        return _parse_items(TrackedItem, result.get("results", []))

    def add_tracked_items(
        self,
        items: list[TrackedItem],
    ) -> AddTrackedItemsResult:
        args = self._build_args(
            items=[item.model_dump(exclude_none=True) for item in items],
        )
        result = self._call_tool(_tools.ADD_TRACKED_ITEMS, args)
        return _parse_item(AddTrackedItemsResult, result)

    def remove_tracked_items(
        self,
        items: list[TrackedItem],
    ) -> RemoveTrackedItemsResult:
        args = self._build_args(
            items=[item.model_dump(exclude_none=True) for item in items],
        )
        result = self._call_tool(_tools.REMOVE_TRACKED_ITEMS, args)
        return _parse_item(RemoveTrackedItemsResult, result)


class AsyncTrackingNamespace(AsyncBaseNamespace):
    async def get_tracked_items(self) -> list[TrackedItem]:
        result = await self._call_tool(_tools.GET_TRACKED_ITEMS, {})
        return _parse_items(TrackedItem, result.get("results", []))

    async def add_tracked_items(
        self,
        items: list[TrackedItem],
    ) -> AddTrackedItemsResult:
        args = self._build_args(
            items=[item.model_dump(exclude_none=True) for item in items],
        )
        result = await self._call_tool(_tools.ADD_TRACKED_ITEMS, args)
        return _parse_item(AddTrackedItemsResult, result)

    async def remove_tracked_items(
        self,
        items: list[TrackedItem],
    ) -> RemoveTrackedItemsResult:
        args = self._build_args(
            items=[item.model_dump(exclude_none=True) for item in items],
        )
        result = await self._call_tool(_tools.REMOVE_TRACKED_ITEMS, args)
        return _parse_item(RemoveTrackedItemsResult, result)
