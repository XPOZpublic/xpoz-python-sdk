from __future__ import annotations

from typing import Any, Type, TypeVar

from pydantic import BaseModel

from xpoz._config import _routes
from xpoz._cursor import AsyncCursorResult, CursorResult
from xpoz._rest import AsyncRestTransport, RestTransport
from xpoz._transform._field_mapping import map_dict_keys_to_snake, map_fields_to_camel
from xpoz.types.instagram import InstagramComment, InstagramPost, InstagramUser

T = TypeVar("T", bound=BaseModel)

CONNECTION_FOLLOWERS = "followers"
CONNECTION_FOLLOWING = "following"
INTERACTION_COMMENTERS = "commenters"
INTERACTION_LIKERS = "likers"


def _csv_fields(fields: list[str] | None) -> str | None:
    converted = map_fields_to_camel(fields)
    if not converted:
        return None
    return ",".join(converted)


_STRING_ID_FIELDS = ("id", "user_id", "post_id")


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


class InstagramLiveNamespace:
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

    def search_posts(
        self,
        query: str,
        *,
        fields: list[str] | None = None,
        cursor: str | None = None,
    ) -> CursorResult[InstagramPost]:
        return self._page(
            InstagramPost,
            _routes.INSTAGRAM_LIVE_POSTS,
            {"q": query, "fields": _csv_fields(fields), "cursor": cursor},
        )

    def get_posts_by_user(
        self,
        identifier: str,
        *,
        fields: list[str] | None = None,
        cursor: str | None = None,
    ) -> CursorResult[InstagramPost]:
        return self._page(
            InstagramPost,
            _routes.INSTAGRAM_LIVE_USER_POSTS.format(identifier=identifier),
            {"fields": _csv_fields(fields), "cursor": cursor},
        )

    def get_post(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
    ) -> InstagramPost | None:
        page = self._page(
            InstagramPost,
            _routes.INSTAGRAM_LIVE_POST.format(post_id=post_id),
            {"fields": _csv_fields(fields)},
        )
        return page.data[0] if page.data else None

    def get_comments(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
        cursor: str | None = None,
    ) -> CursorResult[InstagramComment]:
        return self._page(
            InstagramComment,
            _routes.INSTAGRAM_LIVE_POST_COMMENTS.format(post_id=post_id),
            {"fields": _csv_fields(fields), "cursor": cursor},
        )

    def get_post_interacting_users(
        self,
        post_id: str,
        interaction_type: str,
        *,
        fields: list[str] | None = None,
        cursor: str | None = None,
    ) -> CursorResult[InstagramUser]:
        return self._page(
            InstagramUser,
            _routes.INSTAGRAM_LIVE_POST_INTERACTING_USERS.format(post_id=post_id),
            {
                "interactionType": interaction_type,
                "fields": _csv_fields(fields),
                "cursor": cursor,
            },
        )

    def search_users(
        self,
        name: str,
        *,
        fields: list[str] | None = None,
        cursor: str | None = None,
    ) -> CursorResult[InstagramUser]:
        return self._page(
            InstagramUser,
            _routes.INSTAGRAM_LIVE_USERS,
            {"name": name, "fields": _csv_fields(fields), "cursor": cursor},
        )

    def get_user(
        self,
        identifier: str,
        *,
        fields: list[str] | None = None,
    ) -> InstagramUser | None:
        page = self._page(
            InstagramUser,
            _routes.INSTAGRAM_LIVE_USER.format(identifier=identifier),
            {"fields": _csv_fields(fields)},
        )
        return page.data[0] if page.data else None

    def get_user_connections(
        self,
        identifier: str,
        connection_type: str,
        *,
        fields: list[str] | None = None,
        cursor: str | None = None,
    ) -> CursorResult[InstagramUser]:
        return self._page(
            InstagramUser,
            _routes.INSTAGRAM_LIVE_USER_CONNECTIONS.format(identifier=identifier),
            {
                "connectionType": connection_type,
                "fields": _csv_fields(fields),
                "cursor": cursor,
            },
        )


class AsyncInstagramLiveNamespace:
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

    async def search_posts(
        self,
        query: str,
        *,
        fields: list[str] | None = None,
        cursor: str | None = None,
    ) -> AsyncCursorResult[InstagramPost]:
        return await self._page(
            InstagramPost,
            _routes.INSTAGRAM_LIVE_POSTS,
            {"q": query, "fields": _csv_fields(fields), "cursor": cursor},
        )

    async def get_posts_by_user(
        self,
        identifier: str,
        *,
        fields: list[str] | None = None,
        cursor: str | None = None,
    ) -> AsyncCursorResult[InstagramPost]:
        return await self._page(
            InstagramPost,
            _routes.INSTAGRAM_LIVE_USER_POSTS.format(identifier=identifier),
            {"fields": _csv_fields(fields), "cursor": cursor},
        )

    async def get_post(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
    ) -> InstagramPost | None:
        page = await self._page(
            InstagramPost,
            _routes.INSTAGRAM_LIVE_POST.format(post_id=post_id),
            {"fields": _csv_fields(fields)},
        )
        return page.data[0] if page.data else None

    async def get_comments(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
        cursor: str | None = None,
    ) -> AsyncCursorResult[InstagramComment]:
        return await self._page(
            InstagramComment,
            _routes.INSTAGRAM_LIVE_POST_COMMENTS.format(post_id=post_id),
            {"fields": _csv_fields(fields), "cursor": cursor},
        )

    async def get_post_interacting_users(
        self,
        post_id: str,
        interaction_type: str,
        *,
        fields: list[str] | None = None,
        cursor: str | None = None,
    ) -> AsyncCursorResult[InstagramUser]:
        return await self._page(
            InstagramUser,
            _routes.INSTAGRAM_LIVE_POST_INTERACTING_USERS.format(post_id=post_id),
            {
                "interactionType": interaction_type,
                "fields": _csv_fields(fields),
                "cursor": cursor,
            },
        )

    async def search_users(
        self,
        name: str,
        *,
        fields: list[str] | None = None,
        cursor: str | None = None,
    ) -> AsyncCursorResult[InstagramUser]:
        return await self._page(
            InstagramUser,
            _routes.INSTAGRAM_LIVE_USERS,
            {"name": name, "fields": _csv_fields(fields), "cursor": cursor},
        )

    async def get_user(
        self,
        identifier: str,
        *,
        fields: list[str] | None = None,
    ) -> InstagramUser | None:
        page = await self._page(
            InstagramUser,
            _routes.INSTAGRAM_LIVE_USER.format(identifier=identifier),
            {"fields": _csv_fields(fields)},
        )
        return page.data[0] if page.data else None

    async def get_user_connections(
        self,
        identifier: str,
        connection_type: str,
        *,
        fields: list[str] | None = None,
        cursor: str | None = None,
    ) -> AsyncCursorResult[InstagramUser]:
        return await self._page(
            InstagramUser,
            _routes.INSTAGRAM_LIVE_USER_CONNECTIONS.format(identifier=identifier),
            {
                "connectionType": connection_type,
                "fields": _csv_fields(fields),
                "cursor": cursor,
            },
        )
