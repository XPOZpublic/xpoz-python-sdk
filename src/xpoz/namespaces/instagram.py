from __future__ import annotations

from typing import Any

from xpoz.namespaces._base import BaseNamespace, AsyncBaseNamespace, _parse_item, _parse_items
from xpoz._pagination import PaginatedResult, AsyncPaginatedResult
from xpoz._rest import RestTransport, AsyncRestTransport
from xpoz.namespaces._live_base import _csv_fields, _parse_items as _live_parse_items
from xpoz._config import _routes, _tools
from xpoz._config._constants import ResponseType
from xpoz.types.instagram import InstagramPost, InstagramUser, InstagramComment
from xpoz.types.common import PaginationInfo


class InstagramNamespace(BaseNamespace):
    def __init__(self, call_tool, timeout, rest_transport: RestTransport):
        super().__init__(call_tool, timeout)
        self._rest = rest_transport

    def _cursor_to_paginated_result(
        self,
        payload: dict[str, Any],
        fetch_next: Any,
        page_number: int = 1,
    ) -> PaginatedResult[InstagramUser]:
        items = _live_parse_items(InstagramUser, payload.get("results", []))
        has_more = bool(payload.get("has_more"))
        next_cursor = payload.get("next_page_cursor")

        pagination = PaginationInfo(
            table_name=None,
            total_rows=0,
            total_pages=page_number + 1 if has_more else page_number,
            page_number=page_number,
            page_size=len(items),
            results_count=len(items),
        )

        def fetch_page(_page_number: int, _tbl: str | None) -> PaginatedResult[InstagramUser]:
            if not next_cursor:
                raise IndexError("No more pages available")
            next_payload = fetch_next(next_cursor)
            return self._cursor_to_paginated_result(next_payload, fetch_next, page_number + 1)

        return PaginatedResult(
            data=items,
            pagination=pagination,
            table_name=None,
            export_operation_id=None,
            fetch_page=fetch_page,
            fetch_export=None,
        )

    def get_posts_by_ids(
        self,
        post_ids: list[str],
        *,
        fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> list[InstagramPost]:
        args = self._build_args(
            postIds=post_ids,
            fields=self._convert_fields(fields),
            forceLatest=force_latest,
        )
        result = self._call_and_maybe_poll(_tools.GET_INSTAGRAM_POSTS_BY_IDS, args)
        return _parse_items(InstagramPost, result.get("results", []))

    def get_posts_by_user(
        self,
        identifier: str,
        identifier_type: str = "username",
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        force_latest: bool | None = None,
        response_type: ResponseType | None = None,
        limit: int | None = None,
    ) -> PaginatedResult[InstagramPost]:
        args = self._build_args(
            identifier=identifier,
            identifierType=identifier_type,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            forceLatest=force_latest,
            responseType=response_type,
            limit=limit,
        )
        result = self._call_and_maybe_poll(_tools.GET_INSTAGRAM_POSTS_BY_USER, args)
        return self._build_paginated_result(
            result, InstagramPost, _tools.GET_INSTAGRAM_POSTS_BY_USER, args
        )

    def search_posts(
        self,
        query: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        force_latest: bool | None = None,
        response_type: ResponseType | None = None,
        limit: int | None = None,
    ) -> PaginatedResult[InstagramPost]:
        args = self._build_args(
            query=query,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            forceLatest=force_latest,
            responseType=response_type,
            limit=limit,
        )
        result = self._call_and_maybe_poll(_tools.SEARCH_INSTAGRAM_POSTS, args)
        return self._build_paginated_result(
            result, InstagramPost, _tools.SEARCH_INSTAGRAM_POSTS, args
        )

    def get_comments(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        force_latest: bool | None = None,
    ) -> PaginatedResult[InstagramComment]:
        args = self._build_args(
            postId=post_id,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            forceLatest=force_latest,
        )
        result = self._call_and_maybe_poll(_tools.GET_INSTAGRAM_COMMENTS, args)
        return self._build_paginated_result(
            result, InstagramComment, _tools.GET_INSTAGRAM_COMMENTS, args
        )

    def get_user(
        self,
        identifier: str,
        identifier_type: str = "username",
        *,
        fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> InstagramUser:
        payload = self._rest.get(
            _routes.INSTAGRAM_USER.format(identifier=identifier),
            {
                "identifierType": identifier_type,
                "fields": _csv_fields(fields),
                "forceLatest": "true",
            },
        )
        results = payload.get("results", [])
        if results:
            return _parse_item(InstagramUser, results[0])
        raise ValueError(f"User not found: {identifier}")

    def search_users(
        self,
        name: str,
        *,
        limit: int | None = None,
        fields: list[str] | None = None,
    ) -> list[InstagramUser]:
        payload = self._rest.get(
            _routes.INSTAGRAM_LIVE_USERS,
            {"name": name, "fields": _csv_fields(fields)},
        )
        users = _live_parse_items(InstagramUser, payload.get("results", []))
        if limit and limit > 0:
            return users[:limit]
        return users

    def get_user_connections(
        self,
        username: str,
        connection_type: str,
        *,
        fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> PaginatedResult[InstagramUser]:
        params: dict[str, Any] = {
            "connectionType": connection_type,
            "fields": _csv_fields(fields),
        }
        path = _routes.INSTAGRAM_LIVE_USER_CONNECTIONS.format(identifier=username)
        payload = self._rest.get(path, params)

        def fetch_next(cursor: str) -> dict[str, Any]:
            return self._rest.get(path, {**params, "cursor": cursor})

        return self._cursor_to_paginated_result(payload, fetch_next)

    def get_post_interacting_users(
        self,
        post_id: str,
        interaction_type: str,
        *,
        fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> PaginatedResult[InstagramUser]:
        params: dict[str, Any] = {
            "interactionType": interaction_type,
            "fields": _csv_fields(fields),
        }
        path = _routes.INSTAGRAM_LIVE_POST_INTERACTING_USERS.format(post_id=post_id)
        payload = self._rest.get(path, params)

        def fetch_next(cursor: str) -> dict[str, Any]:
            return self._rest.get(path, {**params, "cursor": cursor})

        return self._cursor_to_paginated_result(payload, fetch_next)

    def get_users_by_keywords(
        self,
        query: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        force_latest: bool | None = None,
        response_type: ResponseType | None = None,
        limit: int | None = None,
    ) -> PaginatedResult[InstagramUser]:
        args = self._build_args(
            query=query,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            forceLatest=force_latest,
            responseType=response_type,
            limit=limit,
        )
        result = self._call_and_maybe_poll(_tools.GET_INSTAGRAM_USERS_BY_KEYWORDS, args)
        return self._build_paginated_result(
            result, InstagramUser, _tools.GET_INSTAGRAM_USERS_BY_KEYWORDS, args
        )


class AsyncInstagramNamespace(AsyncBaseNamespace):
    def __init__(self, call_tool, timeout, rest_transport: AsyncRestTransport):
        super().__init__(call_tool, timeout)
        self._rest = rest_transport

    async def _cursor_to_paginated_result(
        self,
        payload: dict[str, Any],
        fetch_next: Any,
        page_number: int = 1,
    ) -> AsyncPaginatedResult[InstagramUser]:
        items = _live_parse_items(InstagramUser, payload.get("results", []))
        has_more = bool(payload.get("has_more"))
        next_cursor = payload.get("next_page_cursor")

        pagination = PaginationInfo(
            table_name=None,
            total_rows=0,
            total_pages=page_number + 1 if has_more else page_number,
            page_number=page_number,
            page_size=len(items),
            results_count=len(items),
        )

        async def fetch_page(_page_number: int, _tbl: str | None) -> AsyncPaginatedResult[InstagramUser]:
            if not next_cursor:
                raise IndexError("No more pages available")
            next_payload = await fetch_next(next_cursor)
            return await self._cursor_to_paginated_result(next_payload, fetch_next, page_number + 1)

        return AsyncPaginatedResult(
            data=items,
            pagination=pagination,
            table_name=None,
            export_operation_id=None,
            fetch_page=fetch_page,
            fetch_export=None,
        )

    async def get_posts_by_ids(
        self,
        post_ids: list[str],
        *,
        fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> list[InstagramPost]:
        args = self._build_args(
            postIds=post_ids,
            fields=self._convert_fields(fields),
            forceLatest=force_latest,
        )
        result = await self._call_and_maybe_poll(_tools.GET_INSTAGRAM_POSTS_BY_IDS, args)
        return _parse_items(InstagramPost, result.get("results", []))

    async def get_posts_by_user(
        self,
        identifier: str,
        identifier_type: str = "username",
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        force_latest: bool | None = None,
        response_type: ResponseType | None = None,
        limit: int | None = None,
    ) -> AsyncPaginatedResult[InstagramPost]:
        args = self._build_args(
            identifier=identifier,
            identifierType=identifier_type,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            forceLatest=force_latest,
            responseType=response_type,
            limit=limit,
        )
        result = await self._call_and_maybe_poll(_tools.GET_INSTAGRAM_POSTS_BY_USER, args)
        return await self._build_paginated_result(
            result, InstagramPost, _tools.GET_INSTAGRAM_POSTS_BY_USER, args
        )

    async def search_posts(
        self,
        query: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        force_latest: bool | None = None,
        response_type: ResponseType | None = None,
        limit: int | None = None,
    ) -> AsyncPaginatedResult[InstagramPost]:
        args = self._build_args(
            query=query,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            forceLatest=force_latest,
            responseType=response_type,
            limit=limit,
        )
        result = await self._call_and_maybe_poll(_tools.SEARCH_INSTAGRAM_POSTS, args)
        return await self._build_paginated_result(
            result, InstagramPost, _tools.SEARCH_INSTAGRAM_POSTS, args
        )

    async def get_comments(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        force_latest: bool | None = None,
    ) -> AsyncPaginatedResult[InstagramComment]:
        args = self._build_args(
            postId=post_id,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            forceLatest=force_latest,
        )
        result = await self._call_and_maybe_poll(_tools.GET_INSTAGRAM_COMMENTS, args)
        return await self._build_paginated_result(
            result, InstagramComment, _tools.GET_INSTAGRAM_COMMENTS, args
        )

    async def get_user(
        self,
        identifier: str,
        identifier_type: str = "username",
        *,
        fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> InstagramUser:
        payload = await self._rest.get(
            _routes.INSTAGRAM_USER.format(identifier=identifier),
            {
                "identifierType": identifier_type,
                "fields": _csv_fields(fields),
                "forceLatest": "true",
            },
        )
        results = payload.get("results", [])
        if results:
            return _parse_item(InstagramUser, results[0])
        raise ValueError(f"User not found: {identifier}")

    async def search_users(
        self,
        name: str,
        *,
        limit: int | None = None,
        fields: list[str] | None = None,
    ) -> list[InstagramUser]:
        payload = await self._rest.get(
            _routes.INSTAGRAM_LIVE_USERS,
            {"name": name, "fields": _csv_fields(fields)},
        )
        users = _live_parse_items(InstagramUser, payload.get("results", []))
        if limit and limit > 0:
            return users[:limit]
        return users

    async def get_user_connections(
        self,
        username: str,
        connection_type: str,
        *,
        fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> AsyncPaginatedResult[InstagramUser]:
        params: dict[str, Any] = {
            "connectionType": connection_type,
            "fields": _csv_fields(fields),
        }
        path = _routes.INSTAGRAM_LIVE_USER_CONNECTIONS.format(identifier=username)
        payload = await self._rest.get(path, params)

        async def fetch_next(cursor: str) -> dict[str, Any]:
            return await self._rest.get(path, {**params, "cursor": cursor})

        return await self._cursor_to_paginated_result(payload, fetch_next)

    async def get_post_interacting_users(
        self,
        post_id: str,
        interaction_type: str,
        *,
        fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> AsyncPaginatedResult[InstagramUser]:
        params: dict[str, Any] = {
            "interactionType": interaction_type,
            "fields": _csv_fields(fields),
        }
        path = _routes.INSTAGRAM_LIVE_POST_INTERACTING_USERS.format(post_id=post_id)
        payload = await self._rest.get(path, params)

        async def fetch_next(cursor: str) -> dict[str, Any]:
            return await self._rest.get(path, {**params, "cursor": cursor})

        return await self._cursor_to_paginated_result(payload, fetch_next)

    async def get_users_by_keywords(
        self,
        query: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        force_latest: bool | None = None,
        response_type: ResponseType | None = None,
        limit: int | None = None,
    ) -> AsyncPaginatedResult[InstagramUser]:
        args = self._build_args(
            query=query,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            forceLatest=force_latest,
            responseType=response_type,
            limit=limit,
        )
        result = await self._call_and_maybe_poll(_tools.GET_INSTAGRAM_USERS_BY_KEYWORDS, args)
        return await self._build_paginated_result(
            result, InstagramUser, _tools.GET_INSTAGRAM_USERS_BY_KEYWORDS, args
        )


from xpoz._config import _allowed_fields as _af
from xpoz.namespaces._base import _attach_allowed_fields

_INSTAGRAM_FIELD_METADATA: dict[str, dict[str, frozenset[str]]] = {
    "get_user":                   {"fields": _af.GET_INSTAGRAM_USER_FIELDS},
    "search_users":               {"fields": _af.SEARCH_INSTAGRAM_USERS_FIELDS},
    "get_users_by_keywords":      {"fields": _af.GET_INSTAGRAM_USERS_BY_KEYWORDS_FIELDS},
    "get_user_connections":       {"fields": _af.GET_INSTAGRAM_USER_CONNECTIONS_FIELDS},
    "search_posts":               {"fields": _af.SEARCH_INSTAGRAM_POSTS_FIELDS},
    "get_posts_by_user":          {"fields": _af.GET_INSTAGRAM_POSTS_BY_USER_FIELDS},
    "get_posts_by_ids":           {"fields": _af.GET_INSTAGRAM_POSTS_BY_IDS_FIELDS},
    "get_comments":               {"fields": _af.GET_INSTAGRAM_COMMENTS_FIELDS},
    "get_post_interacting_users": {"fields": _af.GET_INSTAGRAM_POST_INTERACTING_USERS_FIELDS},
}

_attach_allowed_fields(InstagramNamespace, _INSTAGRAM_FIELD_METADATA)
_attach_allowed_fields(AsyncInstagramNamespace, _INSTAGRAM_FIELD_METADATA)
