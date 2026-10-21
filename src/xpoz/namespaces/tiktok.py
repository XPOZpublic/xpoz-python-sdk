from __future__ import annotations

from typing import Any

from xpoz.namespaces._base import BaseNamespace, AsyncBaseNamespace, _parse_item, _parse_items
from xpoz._pagination import PaginatedResult, AsyncPaginatedResult
from xpoz._rest import RestTransport, AsyncRestTransport
from xpoz.namespaces._live_base import _csv_fields, _parse_items as _live_parse_items
from xpoz.types.tiktok import TiktokPost, TiktokUser, TiktokComment, TiktokSound
from xpoz.types.common import PaginationInfo
from xpoz._config import _routes, _tools
from xpoz._config._constants import ResponseType


class TiktokNamespace(BaseNamespace):
    def __init__(self, call_tool, timeout, rest_transport: RestTransport):
        super().__init__(call_tool, timeout)
        self._rest = rest_transport

    def _cursor_to_paginated_result(
        self, model: type, payload: dict[str, Any], fetch_next: Any, page_number: int = 1,
    ) -> PaginatedResult:
        items = _live_parse_items(model, payload.get("results", []))
        has_more = bool(payload.get("has_more"))
        next_cursor = payload.get("next_page_cursor")
        pagination = PaginationInfo(
            table_name=None, total_rows=0,
            total_pages=page_number + 1 if has_more else page_number,
            page_number=page_number, page_size=len(items), results_count=len(items),
        )

        def fetch_page(_pn: int, _tbl: str | None) -> PaginatedResult:
            if not next_cursor:
                raise IndexError("No more pages available")
            return self._cursor_to_paginated_result(model, fetch_next(next_cursor), fetch_next, page_number + 1)

        return PaginatedResult(
            data=items, pagination=pagination, table_name=None,
            export_operation_id=None, fetch_page=fetch_page, fetch_export=None,
        )

    def get_posts_by_ids(
        self,
        post_ids: list[str],
        *,
        fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> list[TiktokPost]:
        args = self._build_args(
            postIds=post_ids,
            fields=self._convert_fields(fields),
            forceLatest=force_latest,
        )
        result = self._call_and_maybe_poll(_tools.GET_TIKTOK_POSTS_BY_IDS, args)
        return _parse_items(TiktokPost, result.get("results", []))

    def get_posts_by_user(
        self, identifier: str, identifier_type: str = "username", *,
        fields: list[str] | None = None, start_date: str | None = None,
        end_date: str | None = None, force_latest: bool | None = None,
        response_type: ResponseType | None = None, limit: int | None = None,
    ) -> PaginatedResult[TiktokPost]:
        if response_type == ResponseType.CSV:
            args = self._build_args(
                identifier=identifier, identifierType=identifier_type,
                fields=self._convert_fields(fields), startDate=start_date, endDate=end_date,
                forceLatest=force_latest, responseType=response_type, limit=limit,
            )
            result = self._call_and_maybe_poll(_tools.GET_TIKTOK_POSTS_BY_USER, args)
            return self._build_paginated_result(result, TiktokPost, _tools.GET_TIKTOK_POSTS_BY_USER, args)

        params: dict[str, Any] = {"fields": _csv_fields(fields)}
        path = _routes.TIKTOK_LIVE_USER_POSTS.format(identifier=identifier)
        payload = self._rest.get(path, params)
        def fetch_next(cursor: str) -> dict[str, Any]:
            return self._rest.get(path, {**params, "cursor": cursor})
        return self._cursor_to_paginated_result(TiktokPost, payload, fetch_next)

    def search_posts(
        self, query: str, *, fields: list[str] | None = None,
        start_date: str | None = None, end_date: str | None = None,
        force_latest: bool | None = None, response_type: ResponseType | None = None,
        limit: int | None = None,
    ) -> PaginatedResult[TiktokPost]:
        if response_type == ResponseType.CSV:
            args = self._build_args(
                query=query, fields=self._convert_fields(fields), startDate=start_date,
                endDate=end_date, forceLatest=force_latest, responseType=response_type, limit=limit,
            )
            result = self._call_and_maybe_poll(_tools.SEARCH_TIKTOK_POSTS, args)
            return self._build_paginated_result(result, TiktokPost, _tools.SEARCH_TIKTOK_POSTS, args)

        params: dict[str, Any] = {"q": query, "fields": _csv_fields(fields)}
        payload = self._rest.get(_routes.TIKTOK_LIVE_POSTS, params)
        def fetch_next(cursor: str) -> dict[str, Any]:
            return self._rest.get(_routes.TIKTOK_LIVE_POSTS, {**params, "cursor": cursor})
        return self._cursor_to_paginated_result(TiktokPost, payload, fetch_next)

    def get_comments(
        self, post_id: str, *, fields: list[str] | None = None,
        start_date: str | None = None, end_date: str | None = None,
        force_latest: bool | None = None,
    ) -> PaginatedResult[TiktokComment]:
        params: dict[str, Any] = {"fields": _csv_fields(fields)}
        path = _routes.TIKTOK_LIVE_POST_COMMENTS.format(post_id=post_id)
        payload = self._rest.get(path, params)
        def fetch_next(cursor: str) -> dict[str, Any]:
            return self._rest.get(path, {**params, "cursor": cursor})
        return self._cursor_to_paginated_result(TiktokComment, payload, fetch_next)

    def get_user(
        self, identifier: str, identifier_type: str = "username", *,
        fields: list[str] | None = None, force_latest: bool | None = None,
    ) -> TiktokUser:
        if identifier_type == "id":
            args = self._build_args(
                identifier=identifier, identifierType="id",
                fields=self._convert_fields(fields), forceLatest=force_latest,
            )
            result = self._call_and_maybe_poll(_tools.GET_TIKTOK_USER, args)
            results = result.get("results", [])
            if isinstance(results, list) and len(results) > 0:
                return _parse_item(TiktokUser, results[0])
            return _parse_item(TiktokUser, result)

        payload = self._rest.get(
            _routes.TIKTOK_LIVE_USER.format(identifier=identifier),
            {"fields": _csv_fields(fields)},
        )
        results = _live_parse_items(TiktokUser, payload.get("results", []))
        if results:
            return results[0]
        raise ValueError(f"User not found: {identifier}")

    def search_users(
        self, name: str, *, limit: int | None = None, fields: list[str] | None = None,
    ) -> list[TiktokUser]:
        payload = self._rest.get(
            _routes.TIKTOK_LIVE_USERS,
            {"name": name, "fields": _csv_fields(fields)},
        )
        users = _live_parse_items(TiktokUser, payload.get("results", []))
        if limit and limit > 0:
            return users[:limit]
        return users

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
    ) -> PaginatedResult[TiktokUser]:
        args = self._build_args(
            query=query,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            forceLatest=force_latest,
            responseType=response_type,
            limit=limit,
        )
        result = self._call_and_maybe_poll(_tools.GET_TIKTOK_USERS_BY_KEYWORDS, args)
        return self._build_paginated_result(
            result, TiktokUser, _tools.GET_TIKTOK_USERS_BY_KEYWORDS, args
        )

    def get_posts_by_hashtags(
        self,
        hashtags: list[str],
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        force_latest: bool | None = None,
        response_type: ResponseType | None = None,
        limit: int | None = None,
    ) -> PaginatedResult[TiktokPost]:
        args = self._build_args(
            hashtags=hashtags,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            forceLatest=force_latest,
            responseType=response_type,
            limit=limit,
        )
        result = self._call_and_maybe_poll(_tools.GET_TIKTOK_POSTS_BY_HASHTAGS, args)
        return self._build_paginated_result(
            result, TiktokPost, _tools.GET_TIKTOK_POSTS_BY_HASHTAGS, args
        )

    def get_users_by_hashtags(
        self,
        hashtags: list[str],
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        force_latest: bool | None = None,
        response_type: ResponseType | None = None,
        limit: int | None = None,
    ) -> PaginatedResult[TiktokUser]:
        args = self._build_args(
            hashtags=hashtags,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            forceLatest=force_latest,
            responseType=response_type,
            limit=limit,
        )
        result = self._call_and_maybe_poll(_tools.GET_TIKTOK_USERS_BY_HASHTAGS, args)
        return self._build_paginated_result(
            result, TiktokUser, _tools.GET_TIKTOK_USERS_BY_HASHTAGS, args
        )

    def search_sounds(
        self, keyword: str, *, limit: int | None = None, fields: list[str] | None = None,
    ) -> list[TiktokSound]:
        payload = self._rest.get(
            _routes.TIKTOK_LIVE_SOUNDS,
            {"keyword": keyword, "fields": _csv_fields(fields)},
        )
        sounds = _live_parse_items(TiktokSound, payload.get("results", []))
        if limit and limit > 0:
            return sounds[:limit]
        return sounds

    def get_posts_by_sound(
        self, sound_id: str, *, fields: list[str] | None = None,
        start_date: str | None = None, end_date: str | None = None,
        force_latest: bool | None = None, response_type: ResponseType | None = None,
        limit: int | None = None,
    ) -> PaginatedResult[TiktokPost]:
        if response_type == ResponseType.CSV:
            args = self._build_args(
                soundId=sound_id, fields=self._convert_fields(fields), startDate=start_date,
                endDate=end_date, forceLatest=force_latest, responseType=response_type, limit=limit,
            )
            result = self._call_and_maybe_poll(_tools.GET_TIKTOK_POSTS_BY_SOUND, args)
            return self._build_paginated_result(result, TiktokPost, _tools.GET_TIKTOK_POSTS_BY_SOUND, args)

        params: dict[str, Any] = {"fields": _csv_fields(fields)}
        path = _routes.TIKTOK_LIVE_POSTS_BY_SOUND.format(sound_id=sound_id)
        payload = self._rest.get(path, params)
        def fetch_next(cursor: str) -> dict[str, Any]:
            return self._rest.get(path, {**params, "cursor": cursor})
        return self._cursor_to_paginated_result(TiktokPost, payload, fetch_next)


class AsyncTiktokNamespace(AsyncBaseNamespace):
    def __init__(self, call_tool, timeout, rest_transport: AsyncRestTransport):
        super().__init__(call_tool, timeout)
        self._rest = rest_transport

    async def _cursor_to_paginated_result(
        self, model: type, payload: dict[str, Any], fetch_next: Any, page_number: int = 1,
    ) -> AsyncPaginatedResult:
        items = _live_parse_items(model, payload.get("results", []))
        has_more = bool(payload.get("has_more"))
        next_cursor = payload.get("next_page_cursor")
        pagination = PaginationInfo(
            table_name=None, total_rows=0,
            total_pages=page_number + 1 if has_more else page_number,
            page_number=page_number, page_size=len(items), results_count=len(items),
        )

        async def fetch_page(_pn: int, _tbl: str | None) -> AsyncPaginatedResult:
            if not next_cursor:
                raise IndexError("No more pages available")
            return await self._cursor_to_paginated_result(model, await fetch_next(next_cursor), fetch_next, page_number + 1)

        return AsyncPaginatedResult(
            data=items, pagination=pagination, table_name=None,
            export_operation_id=None, fetch_page=fetch_page, fetch_export=None,
        )

    async def get_posts_by_ids(
        self, post_ids: list[str], *, fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> list[TiktokPost]:
        args = self._build_args(postIds=post_ids, fields=self._convert_fields(fields), forceLatest=force_latest)
        result = await self._call_and_maybe_poll(_tools.GET_TIKTOK_POSTS_BY_IDS, args)
        return _parse_items(TiktokPost, result.get("results", []))

    async def get_posts_by_user(
        self, identifier: str, identifier_type: str = "username", *,
        fields: list[str] | None = None, start_date: str | None = None,
        end_date: str | None = None, force_latest: bool | None = None,
        response_type: ResponseType | None = None, limit: int | None = None,
    ) -> AsyncPaginatedResult[TiktokPost]:
        if response_type == ResponseType.CSV:
            args = self._build_args(
                identifier=identifier, identifierType=identifier_type,
                fields=self._convert_fields(fields), startDate=start_date, endDate=end_date,
                forceLatest=force_latest, responseType=response_type, limit=limit,
            )
            result = await self._call_and_maybe_poll(_tools.GET_TIKTOK_POSTS_BY_USER, args)
            return await self._build_paginated_result(result, TiktokPost, _tools.GET_TIKTOK_POSTS_BY_USER, args)

        params: dict[str, Any] = {"fields": _csv_fields(fields)}
        path = _routes.TIKTOK_LIVE_USER_POSTS.format(identifier=identifier)
        payload = await self._rest.get(path, params)
        async def fetch_next(cursor: str) -> dict[str, Any]:
            return await self._rest.get(path, {**params, "cursor": cursor})
        return await self._cursor_to_paginated_result(TiktokPost, payload, fetch_next)

    async def search_posts(
        self, query: str, *, fields: list[str] | None = None,
        start_date: str | None = None, end_date: str | None = None,
        force_latest: bool | None = None, response_type: ResponseType | None = None,
        limit: int | None = None,
    ) -> AsyncPaginatedResult[TiktokPost]:
        if response_type == ResponseType.CSV:
            args = self._build_args(
                query=query, fields=self._convert_fields(fields), startDate=start_date,
                endDate=end_date, forceLatest=force_latest, responseType=response_type, limit=limit,
            )
            result = await self._call_and_maybe_poll(_tools.SEARCH_TIKTOK_POSTS, args)
            return await self._build_paginated_result(result, TiktokPost, _tools.SEARCH_TIKTOK_POSTS, args)

        params: dict[str, Any] = {"q": query, "fields": _csv_fields(fields)}
        payload = await self._rest.get(_routes.TIKTOK_LIVE_POSTS, params)
        async def fetch_next(cursor: str) -> dict[str, Any]:
            return await self._rest.get(_routes.TIKTOK_LIVE_POSTS, {**params, "cursor": cursor})
        return await self._cursor_to_paginated_result(TiktokPost, payload, fetch_next)

    async def get_comments(
        self, post_id: str, *, fields: list[str] | None = None,
        start_date: str | None = None, end_date: str | None = None,
        force_latest: bool | None = None,
    ) -> AsyncPaginatedResult[TiktokComment]:
        params: dict[str, Any] = {"fields": _csv_fields(fields)}
        path = _routes.TIKTOK_LIVE_POST_COMMENTS.format(post_id=post_id)
        payload = await self._rest.get(path, params)
        async def fetch_next(cursor: str) -> dict[str, Any]:
            return await self._rest.get(path, {**params, "cursor": cursor})
        return await self._cursor_to_paginated_result(TiktokComment, payload, fetch_next)

    async def get_user(
        self, identifier: str, identifier_type: str = "username", *,
        fields: list[str] | None = None, force_latest: bool | None = None,
    ) -> TiktokUser:
        if identifier_type == "id":
            args = self._build_args(
                identifier=identifier, identifierType="id",
                fields=self._convert_fields(fields), forceLatest=force_latest,
            )
            result = await self._call_and_maybe_poll(_tools.GET_TIKTOK_USER, args)
            results = result.get("results", [])
            if isinstance(results, list) and len(results) > 0:
                return _parse_item(TiktokUser, results[0])
            return _parse_item(TiktokUser, result)

        payload = await self._rest.get(
            _routes.TIKTOK_LIVE_USER.format(identifier=identifier),
            {"fields": _csv_fields(fields)},
        )
        results = _live_parse_items(TiktokUser, payload.get("results", []))
        if results:
            return results[0]
        raise ValueError(f"User not found: {identifier}")

    async def search_users(
        self, name: str, *, limit: int | None = None, fields: list[str] | None = None,
    ) -> list[TiktokUser]:
        payload = await self._rest.get(
            _routes.TIKTOK_LIVE_USERS,
            {"name": name, "fields": _csv_fields(fields)},
        )
        users = _live_parse_items(TiktokUser, payload.get("results", []))
        if limit and limit > 0:
            return users[:limit]
        return users

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
    ) -> AsyncPaginatedResult[TiktokUser]:
        args = self._build_args(
            query=query,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            forceLatest=force_latest,
            responseType=response_type,
            limit=limit,
        )
        result = await self._call_and_maybe_poll(_tools.GET_TIKTOK_USERS_BY_KEYWORDS, args)
        return await self._build_paginated_result(
            result, TiktokUser, _tools.GET_TIKTOK_USERS_BY_KEYWORDS, args
        )

    async def get_posts_by_hashtags(
        self,
        hashtags: list[str],
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        force_latest: bool | None = None,
        response_type: ResponseType | None = None,
        limit: int | None = None,
    ) -> AsyncPaginatedResult[TiktokPost]:
        args = self._build_args(
            hashtags=hashtags,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            forceLatest=force_latest,
            responseType=response_type,
            limit=limit,
        )
        result = await self._call_and_maybe_poll(_tools.GET_TIKTOK_POSTS_BY_HASHTAGS, args)
        return await self._build_paginated_result(
            result, TiktokPost, _tools.GET_TIKTOK_POSTS_BY_HASHTAGS, args
        )

    async def get_users_by_hashtags(
        self,
        hashtags: list[str],
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        force_latest: bool | None = None,
        response_type: ResponseType | None = None,
        limit: int | None = None,
    ) -> AsyncPaginatedResult[TiktokUser]:
        args = self._build_args(
            hashtags=hashtags,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            forceLatest=force_latest,
            responseType=response_type,
            limit=limit,
        )
        result = await self._call_and_maybe_poll(_tools.GET_TIKTOK_USERS_BY_HASHTAGS, args)
        return await self._build_paginated_result(
            result, TiktokUser, _tools.GET_TIKTOK_USERS_BY_HASHTAGS, args
        )

    async def search_sounds(
        self, keyword: str, *, limit: int | None = None, fields: list[str] | None = None,
    ) -> list[TiktokSound]:
        payload = await self._rest.get(
            _routes.TIKTOK_LIVE_SOUNDS,
            {"keyword": keyword, "fields": _csv_fields(fields)},
        )
        sounds = _live_parse_items(TiktokSound, payload.get("results", []))
        if limit and limit > 0:
            return sounds[:limit]
        return sounds

    async def get_posts_by_sound(
        self, sound_id: str, *, fields: list[str] | None = None,
        start_date: str | None = None, end_date: str | None = None,
        force_latest: bool | None = None, response_type: ResponseType | None = None,
        limit: int | None = None,
    ) -> AsyncPaginatedResult[TiktokPost]:
        if response_type == ResponseType.CSV:
            args = self._build_args(
                soundId=sound_id, fields=self._convert_fields(fields), startDate=start_date,
                endDate=end_date, forceLatest=force_latest, responseType=response_type, limit=limit,
            )
            result = await self._call_and_maybe_poll(_tools.GET_TIKTOK_POSTS_BY_SOUND, args)
            return await self._build_paginated_result(result, TiktokPost, _tools.GET_TIKTOK_POSTS_BY_SOUND, args)

        params: dict[str, Any] = {"fields": _csv_fields(fields)}
        path = _routes.TIKTOK_LIVE_POSTS_BY_SOUND.format(sound_id=sound_id)
        payload = await self._rest.get(path, params)
        async def fetch_next(cursor: str) -> dict[str, Any]:
            return await self._rest.get(path, {**params, "cursor": cursor})
        return await self._cursor_to_paginated_result(TiktokPost, payload, fetch_next)


from xpoz._config import _allowed_fields as _af
from xpoz.namespaces._base import _attach_allowed_fields

_TIKTOK_FIELD_METADATA: dict[str, dict[str, frozenset[str]]] = {
    "get_user":              {"fields": _af.GET_TIKTOK_USER_FIELDS},
    "search_users":          {"fields": _af.SEARCH_TIKTOK_USERS_FIELDS},
    "get_users_by_keywords": {"fields": _af.GET_TIKTOK_USERS_BY_KEYWORDS_FIELDS},
    "get_users_by_hashtags": {"fields": _af.GET_TIKTOK_USERS_BY_HASHTAGS_FIELDS},
    "search_posts":          {"fields": _af.SEARCH_TIKTOK_POSTS_FIELDS},
    "get_posts_by_user":     {"fields": _af.GET_TIKTOK_POSTS_BY_USER_FIELDS},
    "get_posts_by_ids":      {"fields": _af.GET_TIKTOK_POSTS_BY_IDS_FIELDS},
    "get_posts_by_hashtags": {"fields": _af.GET_TIKTOK_POSTS_BY_HASHTAGS_FIELDS},
    "get_comments":          {"fields": _af.GET_TIKTOK_COMMENTS_FIELDS},
    "search_sounds":         {"fields": _af.SEARCH_TIKTOK_SOUNDS_FIELDS},
    "get_posts_by_sound":    {"fields": _af.GET_TIKTOK_POSTS_BY_SOUND_FIELDS},
}

_attach_allowed_fields(TiktokNamespace, _TIKTOK_FIELD_METADATA)
_attach_allowed_fields(AsyncTiktokNamespace, _TIKTOK_FIELD_METADATA)
