from __future__ import annotations

from typing import Any

from xpoz.namespaces._base import BaseNamespace, AsyncBaseNamespace, _parse_item, _parse_items
from xpoz._pagination import PaginatedResult, AsyncPaginatedResult
from xpoz._results import NoDataResult
from xpoz.types.tiktok import TiktokPost, TiktokUser, TiktokComment
from xpoz._config import _tools
from xpoz._config._constants import ResponseType


class TiktokNamespace(BaseNamespace):
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
    ) -> PaginatedResult[TiktokPost] | NoDataResult:
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
        result = self._call_and_maybe_poll(_tools.GET_TIKTOK_POSTS_BY_USER, args)
        return self._build_paginated_result(
            result, TiktokPost, _tools.GET_TIKTOK_POSTS_BY_USER, args
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
    ) -> PaginatedResult[TiktokPost] | NoDataResult:
        args = self._build_args(
            query=query,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            forceLatest=force_latest,
            responseType=response_type,
            limit=limit,
        )
        result = self._call_and_maybe_poll(_tools.SEARCH_TIKTOK_POSTS, args)
        return self._build_paginated_result(
            result, TiktokPost, _tools.SEARCH_TIKTOK_POSTS, args
        )

    def get_comments(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        force_latest: bool | None = None,
    ) -> PaginatedResult[TiktokComment] | NoDataResult:
        args = self._build_args(
            postId=post_id,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            forceLatest=force_latest,
        )
        result = self._call_and_maybe_poll(_tools.GET_TIKTOK_COMMENTS, args)
        return self._build_paginated_result(
            result, TiktokComment, _tools.GET_TIKTOK_COMMENTS, args
        )

    def get_user(
        self,
        identifier: str,
        identifier_type: str = "username",
        *,
        fields: list[str] | None = None,
    ) -> TiktokUser:
        args = self._build_args(
            identifier=identifier,
            identifierType=identifier_type,
            fields=self._convert_fields(fields),
        )
        result = self._call_and_maybe_poll(_tools.GET_TIKTOK_USER, args)
        results = result.get("results", [])
        if isinstance(results, list) and len(results) > 0:
            return _parse_item(TiktokUser, results[0])
        return _parse_item(TiktokUser, result)

    def search_users(
        self,
        name: str,
        *,
        limit: int | None = None,
        fields: list[str] | None = None,
    ) -> list[TiktokUser]:
        args = self._build_args(
            name=name,
            limit=limit,
            fields=self._convert_fields(fields),
        )
        result = self._call_and_maybe_poll(_tools.SEARCH_TIKTOK_USERS, args)
        return _parse_items(TiktokUser, result.get("results", []))

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
    ) -> PaginatedResult[TiktokUser] | NoDataResult:
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


class AsyncTiktokNamespace(AsyncBaseNamespace):
    async def get_posts_by_ids(
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
        result = await self._call_and_maybe_poll(_tools.GET_TIKTOK_POSTS_BY_IDS, args)
        return _parse_items(TiktokPost, result.get("results", []))

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
    ) -> AsyncPaginatedResult[TiktokPost] | NoDataResult:
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
        result = await self._call_and_maybe_poll(_tools.GET_TIKTOK_POSTS_BY_USER, args)
        return await self._build_paginated_result(
            result, TiktokPost, _tools.GET_TIKTOK_POSTS_BY_USER, args
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
    ) -> AsyncPaginatedResult[TiktokPost] | NoDataResult:
        args = self._build_args(
            query=query,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            forceLatest=force_latest,
            responseType=response_type,
            limit=limit,
        )
        result = await self._call_and_maybe_poll(_tools.SEARCH_TIKTOK_POSTS, args)
        return await self._build_paginated_result(
            result, TiktokPost, _tools.SEARCH_TIKTOK_POSTS, args
        )

    async def get_comments(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        force_latest: bool | None = None,
    ) -> AsyncPaginatedResult[TiktokComment] | NoDataResult:
        args = self._build_args(
            postId=post_id,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            forceLatest=force_latest,
        )
        result = await self._call_and_maybe_poll(_tools.GET_TIKTOK_COMMENTS, args)
        return await self._build_paginated_result(
            result, TiktokComment, _tools.GET_TIKTOK_COMMENTS, args
        )

    async def get_user(
        self,
        identifier: str,
        identifier_type: str = "username",
        *,
        fields: list[str] | None = None,
    ) -> TiktokUser:
        args = self._build_args(
            identifier=identifier,
            identifierType=identifier_type,
            fields=self._convert_fields(fields),
        )
        result = await self._call_and_maybe_poll(_tools.GET_TIKTOK_USER, args)
        results = result.get("results", [])
        if isinstance(results, list) and len(results) > 0:
            return _parse_item(TiktokUser, results[0])
        return _parse_item(TiktokUser, result)

    async def search_users(
        self,
        name: str,
        *,
        limit: int | None = None,
        fields: list[str] | None = None,
    ) -> list[TiktokUser]:
        args = self._build_args(
            name=name,
            limit=limit,
            fields=self._convert_fields(fields),
        )
        result = await self._call_and_maybe_poll(_tools.SEARCH_TIKTOK_USERS, args)
        return _parse_items(TiktokUser, result.get("results", []))

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
    ) -> AsyncPaginatedResult[TiktokUser] | NoDataResult:
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
