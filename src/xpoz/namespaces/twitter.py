from __future__ import annotations

from typing import Any

from xpoz.namespaces._base import BaseNamespace, AsyncBaseNamespace, _parse_item, _parse_items
from xpoz._pagination import PaginatedResult, AsyncPaginatedResult
from xpoz._rest import RestTransport, AsyncRestTransport
from xpoz.namespaces._live_base import _csv_fields, _parse_items as _live_parse_items
from xpoz.types.twitter import TwitterPost, TwitterUser
from xpoz.types.common import PaginationInfo
from xpoz._config import _routes, _tools
from xpoz._config._constants import ResponseType


class TwitterNamespace(BaseNamespace):
    def __init__(self, call_tool, timeout, rest_transport: RestTransport):
        super().__init__(call_tool, timeout)
        self._rest = rest_transport

    def _cursor_to_paginated_result(
        self,
        model: type,
        payload: dict[str, Any],
        fetch_next: Any,
        page_number: int = 1,
    ) -> PaginatedResult:
        items = _live_parse_items(model, payload.get("results", []))
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

        def fetch_page(_page_number: int, _tbl: str | None) -> PaginatedResult:
            if not next_cursor:
                raise IndexError("No more pages available")
            next_payload = fetch_next(next_cursor)
            return self._cursor_to_paginated_result(model, next_payload, fetch_next, page_number + 1)

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
    ) -> list[TwitterPost]:
        args = self._build_args(
            postIds=post_ids,
            fields=self._convert_fields(fields),
            forceLatest=force_latest,
        )
        result = self._call_and_maybe_poll(_tools.GET_TWITTER_POSTS_BY_IDS, args)
        return _parse_items(TwitterPost, result.get("results", []))

    def get_posts_by_author(
        self,
        identifier: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        force_latest: bool | None = None,
        response_type: ResponseType | None = None,
        limit: int | None = None,
    ) -> PaginatedResult[TwitterPost]:
        if response_type == ResponseType.CSV:
            args = self._build_args(
                username=identifier,
                fields=self._convert_fields(fields),
                startDate=start_date,
                endDate=end_date,
                forceLatest=force_latest,
                responseType=response_type,
                limit=limit,
            )
            result = self._call_and_maybe_poll(_tools.GET_TWITTER_POSTS_BY_AUTHOR, args)
            return self._build_paginated_result(result, TwitterPost, _tools.GET_TWITTER_POSTS_BY_AUTHOR, args)

        params: dict[str, Any] = {
            "since": start_date,
            "until": end_date,
            "fields": _csv_fields(fields),
        }
        path = _routes.TWITTER_LIVE_USER_POSTS.format(username=identifier)
        payload = self._rest.get(path, params)

        def fetch_next(cursor: str) -> dict[str, Any]:
            return self._rest.get(path, {**params, "cursor": cursor})

        return self._cursor_to_paginated_result(TwitterPost, payload, fetch_next)

    def search_posts(
        self,
        query: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        author_username: str | None = None,
        author_id: str | None = None,
        language: str | None = None,
        filter_out_retweets: bool | None = None,
        force_latest: bool | None = None,
        response_type: ResponseType | None = None,
        limit: int | None = None,
    ) -> PaginatedResult[TwitterPost]:
        args = self._build_args(
            query=query,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            authorUsername=author_username,
            authorId=author_id,
            language=language,
            filterOutRetweets=filter_out_retweets,
            forceLatest=force_latest,
            responseType=response_type,
            limit=limit,
        )
        if response_type == "csv":
            raw = self._call_tool(_tools.SEARCH_TWITTER_POSTS, args)
            export_op_id = raw.get("operationId") or raw.get("dataDumpExportOperationId")
            csv_raw: dict[str, Any] = {
                "results": [],
                "dataDumpExportOperationId": export_op_id,
            }
            return self._build_paginated_result(csv_raw, TwitterPost, _tools.SEARCH_TWITTER_POSTS, args)
        result = self._call_and_maybe_poll(_tools.SEARCH_TWITTER_POSTS, args)
        return self._build_paginated_result(result, TwitterPost, _tools.SEARCH_TWITTER_POSTS, args)

    def get_retweets(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
    ) -> PaginatedResult[TwitterPost]:
        args = self._build_args(
            postId=post_id,
            fields=self._convert_fields(fields),
            startDate=start_date,
        )
        result = self._call_and_maybe_poll(_tools.GET_TWITTER_RETWEETS, args)
        return self._build_paginated_result(result, TwitterPost, _tools.GET_TWITTER_RETWEETS, args)

    def get_quotes(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        force_latest: bool | None = None,
    ) -> PaginatedResult[TwitterPost]:
        params: dict[str, Any] = {"fields": _csv_fields(fields)}
        path = _routes.TWITTER_LIVE_POST_QUOTES.format(post_id=post_id)
        payload = self._rest.get(path, params)

        def fetch_next(cursor: str) -> dict[str, Any]:
            return self._rest.get(path, {**params, "cursor": cursor})

        return self._cursor_to_paginated_result(TwitterPost, payload, fetch_next)

    def get_comments(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        force_latest: bool | None = None,
    ) -> PaginatedResult[TwitterPost]:
        params: dict[str, Any] = {"fields": _csv_fields(fields)}
        path = _routes.TWITTER_LIVE_POST_COMMENTS.format(post_id=post_id)
        payload = self._rest.get(path, params)

        def fetch_next(cursor: str) -> dict[str, Any]:
            return self._rest.get(path, {**params, "cursor": cursor})

        return self._cursor_to_paginated_result(TwitterPost, payload, fetch_next)

    def get_post_interacting_users(
        self,
        post_id: str,
        interaction_type: str,
        *,
        fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> PaginatedResult[TwitterUser]:
        params: dict[str, Any] = {
            "interactionType": interaction_type,
            "fields": _csv_fields(fields),
        }
        path = _routes.TWITTER_LIVE_POST_INTERACTING_USERS.format(post_id=post_id)
        payload = self._rest.get(path, params)

        def fetch_next(cursor: str) -> dict[str, Any]:
            return self._rest.get(path, {**params, "cursor": cursor})

        return self._cursor_to_paginated_result(TwitterUser, payload, fetch_next)

    def count_posts(
        self,
        phrase: str,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> int:
        args = self._build_args(
            phrase=phrase,
            startDate=start_date,
            endDate=end_date,
        )
        result = self._call_and_maybe_poll(_tools.COUNT_TWEETS, args)
        count = result.get("results", result.get("count", 0))
        if isinstance(count, list):
            if len(count) == 0:
                return 0
            first = count[0]
            if isinstance(first, dict):
                return int(next(iter(first.values())))
            return int(first)
        return int(count)

    def get_users(
        self,
        identifiers: list[str],
        identifier_type: str = "username",
        *,
        fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> list[TwitterUser]:
        args = self._build_args(
            identifiers=identifiers,
            identifierType=identifier_type,
            fields=self._convert_fields(fields),
            forceLatest=force_latest,
        )
        result = self._call_and_maybe_poll(_tools.GET_TWITTER_USERS, args)
        return _parse_items(TwitterUser, result.get("results", []))

    def get_user(
        self,
        identifier: str,
        identifier_type: str = "username",
        *,
        fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> TwitterUser:
        if identifier_type == "id":
            args = self._build_args(
                identifier=identifier,
                identifierType="id",
                fields=self._convert_fields(fields),
                forceLatest=force_latest,
            )
            result = self._call_and_maybe_poll(_tools.GET_TWITTER_USER, args)
            results = result.get("results", [])
            if isinstance(results, list) and len(results) > 0:
                return _parse_item(TwitterUser, results[0])
            return _parse_item(TwitterUser, result)

        payload = self._rest.get(
            _routes.TWITTER_LIVE_USER.format(username=identifier),
            {"fields": _csv_fields(fields)},
        )
        results = payload.get("results", [])
        if results:
            return _live_parse_items(TwitterUser, results)[0]
        raise ValueError(f"User not found: {identifier}")

    def search_users(
        self,
        name: str,
        *,
        limit: int | None = None,
        fields: list[str] | None = None,
    ) -> list[TwitterUser]:
        payload = self._rest.get(
            _routes.TWITTER_LIVE_USERS,
            {"q": name, "fields": _csv_fields(fields)},
        )
        users = _live_parse_items(TwitterUser, payload.get("results", []))
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
    ) -> PaginatedResult[TwitterUser]:
        params: dict[str, Any] = {
            "connectionType": connection_type,
            "fields": _csv_fields(fields),
        }
        path = _routes.TWITTER_LIVE_USER_CONNECTIONS.format(username=username)
        payload = self._rest.get(path, params)

        def fetch_next(cursor: str) -> dict[str, Any]:
            return self._rest.get(path, {**params, "cursor": cursor})

        return self._cursor_to_paginated_result(TwitterUser, payload, fetch_next)

    def get_users_by_keywords(
        self,
        query: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        language: str | None = None,
        force_latest: bool | None = None,
        response_type: ResponseType | None = None,
        limit: int | None = None,
    ) -> PaginatedResult[TwitterUser]:
        args = self._build_args(
            query=query,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            language=language,
            forceLatest=force_latest,
            responseType=response_type,
            limit=limit,
        )
        result = self._call_and_maybe_poll(_tools.GET_TWITTER_USERS_BY_KEYWORDS, args)
        return self._build_paginated_result(result, TwitterUser, _tools.GET_TWITTER_USERS_BY_KEYWORDS, args)


class AsyncTwitterNamespace(AsyncBaseNamespace):
    def __init__(self, call_tool, timeout, rest_transport: AsyncRestTransport):
        super().__init__(call_tool, timeout)
        self._rest = rest_transport

    async def _cursor_to_paginated_result(
        self,
        model: type,
        payload: dict[str, Any],
        fetch_next: Any,
        page_number: int = 1,
    ) -> AsyncPaginatedResult:
        items = _live_parse_items(model, payload.get("results", []))
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

        async def fetch_page(_page_number: int, _tbl: str | None) -> AsyncPaginatedResult:
            if not next_cursor:
                raise IndexError("No more pages available")
            next_payload = await fetch_next(next_cursor)
            return await self._cursor_to_paginated_result(model, next_payload, fetch_next, page_number + 1)

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
    ) -> list[TwitterPost]:
        args = self._build_args(
            postIds=post_ids,
            fields=self._convert_fields(fields),
            forceLatest=force_latest,
        )
        result = await self._call_and_maybe_poll(_tools.GET_TWITTER_POSTS_BY_IDS, args)
        return _parse_items(TwitterPost, result.get("results", []))

    async def get_posts_by_author(
        self,
        identifier: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        force_latest: bool | None = None,
        response_type: ResponseType | None = None,
        limit: int | None = None,
    ) -> AsyncPaginatedResult[TwitterPost]:
        if response_type == ResponseType.CSV:
            args = self._build_args(
                username=identifier,
                fields=self._convert_fields(fields),
                startDate=start_date,
                endDate=end_date,
                forceLatest=force_latest,
                responseType=response_type,
                limit=limit,
            )
            result = await self._call_and_maybe_poll(_tools.GET_TWITTER_POSTS_BY_AUTHOR, args)
            return await self._build_paginated_result(result, TwitterPost, _tools.GET_TWITTER_POSTS_BY_AUTHOR, args)

        params: dict[str, Any] = {
            "since": start_date,
            "until": end_date,
            "fields": _csv_fields(fields),
        }
        path = _routes.TWITTER_LIVE_USER_POSTS.format(username=identifier)
        payload = await self._rest.get(path, params)

        async def fetch_next(cursor: str) -> dict[str, Any]:
            return await self._rest.get(path, {**params, "cursor": cursor})

        return await self._cursor_to_paginated_result(TwitterPost, payload, fetch_next)

    async def search_posts(
        self,
        query: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        author_username: str | None = None,
        author_id: str | None = None,
        language: str | None = None,
        filter_out_retweets: bool | None = None,
        force_latest: bool | None = None,
        response_type: ResponseType | None = None,
        limit: int | None = None,
    ) -> AsyncPaginatedResult[TwitterPost]:
        args = self._build_args(
            query=query,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            authorUsername=author_username,
            authorId=author_id,
            language=language,
            filterOutRetweets=filter_out_retweets,
            forceLatest=force_latest,
            responseType=response_type,
            limit=limit,
        )
        if response_type == "csv":
            raw = await self._call_tool(_tools.SEARCH_TWITTER_POSTS, args)
            export_op_id = raw.get("operationId") or raw.get("dataDumpExportOperationId")
            csv_raw: dict[str, Any] = {
                "results": [],
                "dataDumpExportOperationId": export_op_id,
            }
            return await self._build_paginated_result(csv_raw, TwitterPost, _tools.SEARCH_TWITTER_POSTS, args)
        result = await self._call_and_maybe_poll(_tools.SEARCH_TWITTER_POSTS, args)
        return await self._build_paginated_result(result, TwitterPost, _tools.SEARCH_TWITTER_POSTS, args)

    async def get_retweets(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
    ) -> AsyncPaginatedResult[TwitterPost]:
        args = self._build_args(
            postId=post_id,
            fields=self._convert_fields(fields),
            startDate=start_date,
        )
        result = await self._call_and_maybe_poll(_tools.GET_TWITTER_RETWEETS, args)
        return await self._build_paginated_result(result, TwitterPost, _tools.GET_TWITTER_RETWEETS, args)

    async def get_quotes(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        force_latest: bool | None = None,
    ) -> AsyncPaginatedResult[TwitterPost]:
        params: dict[str, Any] = {"fields": _csv_fields(fields)}
        path = _routes.TWITTER_LIVE_POST_QUOTES.format(post_id=post_id)
        payload = await self._rest.get(path, params)

        async def fetch_next(cursor: str) -> dict[str, Any]:
            return await self._rest.get(path, {**params, "cursor": cursor})

        return await self._cursor_to_paginated_result(TwitterPost, payload, fetch_next)

    async def get_comments(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        force_latest: bool | None = None,
    ) -> AsyncPaginatedResult[TwitterPost]:
        params: dict[str, Any] = {"fields": _csv_fields(fields)}
        path = _routes.TWITTER_LIVE_POST_COMMENTS.format(post_id=post_id)
        payload = await self._rest.get(path, params)

        async def fetch_next(cursor: str) -> dict[str, Any]:
            return await self._rest.get(path, {**params, "cursor": cursor})

        return await self._cursor_to_paginated_result(TwitterPost, payload, fetch_next)

    async def get_post_interacting_users(
        self,
        post_id: str,
        interaction_type: str,
        *,
        fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> AsyncPaginatedResult[TwitterUser]:
        params: dict[str, Any] = {
            "interactionType": interaction_type,
            "fields": _csv_fields(fields),
        }
        path = _routes.TWITTER_LIVE_POST_INTERACTING_USERS.format(post_id=post_id)
        payload = await self._rest.get(path, params)

        async def fetch_next(cursor: str) -> dict[str, Any]:
            return await self._rest.get(path, {**params, "cursor": cursor})

        return await self._cursor_to_paginated_result(TwitterUser, payload, fetch_next)

    async def count_posts(
        self,
        phrase: str,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> int:
        args = self._build_args(
            phrase=phrase,
            startDate=start_date,
            endDate=end_date,
        )
        result = await self._call_and_maybe_poll(_tools.COUNT_TWEETS, args)
        count = result.get("results", result.get("count", 0))
        if isinstance(count, list):
            if len(count) == 0:
                return 0
            first = count[0]
            if isinstance(first, dict):
                return int(next(iter(first.values())))
            return int(first)
        return int(count)

    async def get_users(
        self,
        identifiers: list[str],
        identifier_type: str = "username",
        *,
        fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> list[TwitterUser]:
        args = self._build_args(
            identifiers=identifiers,
            identifierType=identifier_type,
            fields=self._convert_fields(fields),
            forceLatest=force_latest,
        )
        result = await self._call_and_maybe_poll(_tools.GET_TWITTER_USERS, args)
        return _parse_items(TwitterUser, result.get("results", []))

    async def get_user(
        self,
        identifier: str,
        identifier_type: str = "username",
        *,
        fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> TwitterUser:
        if identifier_type == "id":
            args = self._build_args(
                identifier=identifier,
                identifierType="id",
                fields=self._convert_fields(fields),
                forceLatest=force_latest,
            )
            result = await self._call_and_maybe_poll(_tools.GET_TWITTER_USER, args)
            results = result.get("results", [])
            if isinstance(results, list) and len(results) > 0:
                return _parse_item(TwitterUser, results[0])
            return _parse_item(TwitterUser, result)

        payload = await self._rest.get(
            _routes.TWITTER_LIVE_USER.format(username=identifier),
            {"fields": _csv_fields(fields)},
        )
        results = payload.get("results", [])
        if results:
            return _live_parse_items(TwitterUser, results)[0]
        raise ValueError(f"User not found: {identifier}")

    async def search_users(
        self,
        name: str,
        *,
        limit: int | None = None,
        fields: list[str] | None = None,
    ) -> list[TwitterUser]:
        payload = await self._rest.get(
            _routes.TWITTER_LIVE_USERS,
            {"q": name, "fields": _csv_fields(fields)},
        )
        users = _live_parse_items(TwitterUser, payload.get("results", []))
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
    ) -> AsyncPaginatedResult[TwitterUser]:
        params: dict[str, Any] = {
            "connectionType": connection_type,
            "fields": _csv_fields(fields),
        }
        path = _routes.TWITTER_LIVE_USER_CONNECTIONS.format(username=username)
        payload = await self._rest.get(path, params)

        async def fetch_next(cursor: str) -> dict[str, Any]:
            return await self._rest.get(path, {**params, "cursor": cursor})

        return await self._cursor_to_paginated_result(TwitterUser, payload, fetch_next)

    async def get_users_by_keywords(
        self,
        query: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        language: str | None = None,
        force_latest: bool | None = None,
        response_type: ResponseType | None = None,
        limit: int | None = None,
    ) -> AsyncPaginatedResult[TwitterUser]:
        args = self._build_args(
            query=query,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            language=language,
            forceLatest=force_latest,
            responseType=response_type,
            limit=limit,
        )
        result = await self._call_and_maybe_poll(_tools.GET_TWITTER_USERS_BY_KEYWORDS, args)
        return await self._build_paginated_result(result, TwitterUser, _tools.GET_TWITTER_USERS_BY_KEYWORDS, args)


from xpoz._config import _allowed_fields as _af
from xpoz.namespaces._base import _attach_allowed_fields

_TWITTER_FIELD_METADATA: dict[str, dict[str, frozenset[str]]] = {
    "get_user":                   {"fields": _af.GET_TWITTER_USER_FIELDS},
    "get_users":                  {"fields": _af.GET_TWITTER_USERS_FIELDS},
    "search_users":               {"fields": _af.SEARCH_TWITTER_USERS_FIELDS},
    "get_users_by_keywords":      {"fields": _af.GET_TWITTER_USERS_BY_KEYWORDS_FIELDS},
    "get_user_connections":       {"fields": _af.GET_TWITTER_USER_CONNECTIONS_FIELDS},
    "search_posts":               {"fields": _af.SEARCH_TWITTER_POSTS_FIELDS},
    "get_posts_by_author":        {"fields": _af.GET_TWITTER_POSTS_BY_AUTHOR_FIELDS},
    "get_posts_by_ids":           {"fields": _af.GET_TWITTER_POSTS_BY_IDS_FIELDS},
    "get_comments":               {"fields": _af.GET_TWITTER_COMMENTS_FIELDS},
    "get_quotes":                 {"fields": _af.GET_TWITTER_QUOTES_FIELDS},
    "get_retweets":                {"fields": _af.GET_TWITTER_RETWEETS_FIELDS},
    "get_post_interacting_users": {"fields": _af.GET_TWITTER_POST_INTERACTING_USERS_FIELDS},
}

_attach_allowed_fields(TwitterNamespace, _TWITTER_FIELD_METADATA)
_attach_allowed_fields(AsyncTwitterNamespace, _TWITTER_FIELD_METADATA)
