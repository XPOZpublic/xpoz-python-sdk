from __future__ import annotations

from typing import Any

from xpoz.namespaces._base import BaseNamespace, AsyncBaseNamespace, _parse_item, _parse_items
from xpoz._pagination import PaginatedResult, AsyncPaginatedResult
from xpoz.types.instagram import InstagramPost, InstagramUser, InstagramComment


class InstagramNamespace(BaseNamespace):
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
        result = self._call_and_maybe_poll("getInstagramPostsByIds", args)
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
    ) -> PaginatedResult[InstagramPost]:
        args = self._build_args(
            identifier=identifier,
            identifierType=identifier_type,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            forceLatest=force_latest,
        )
        result = self._call_and_maybe_poll("getInstagramPostsByUser", args)
        return self._build_paginated_result(
            result, InstagramPost, "getInstagramPostsByUser", args
        )

    def search_posts(
        self,
        query: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        force_latest: bool | None = None,
    ) -> PaginatedResult[InstagramPost]:
        args = self._build_args(
            query=query,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            forceLatest=force_latest,
        )
        result = self._call_and_maybe_poll("getInstagramPostsByKeywords", args)
        return self._build_paginated_result(
            result, InstagramPost, "getInstagramPostsByKeywords", args
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
        result = self._call_and_maybe_poll("getInstagramCommentsByPostId", args)
        return self._build_paginated_result(
            result, InstagramComment, "getInstagramCommentsByPostId", args
        )

    def get_user(
        self,
        identifier: str,
        identifier_type: str = "username",
        *,
        fields: list[str] | None = None,
    ) -> InstagramUser:
        args = self._build_args(
            identifier=identifier,
            identifierType=identifier_type,
            fields=self._convert_fields(fields),
        )
        result = self._call_and_maybe_poll("getInstagramUser", args)
        results = result.get("results", [])
        if isinstance(results, list) and len(results) > 0:
            return _parse_item(InstagramUser, results[0])
        return _parse_item(InstagramUser, result)

    def search_users(
        self,
        name: str,
        *,
        limit: int | None = None,
        fields: list[str] | None = None,
    ) -> list[InstagramUser]:
        args = self._build_args(
            name=name,
            limit=limit,
            fields=self._convert_fields(fields),
        )
        result = self._call_and_maybe_poll("searchInstagramUsers", args)
        return _parse_items(InstagramUser, result.get("results", []))

    def get_user_connections(
        self,
        username: str,
        connection_type: str,
        *,
        fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> PaginatedResult[InstagramUser]:
        args = self._build_args(
            username=username,
            connectionType=connection_type,
            fields=self._convert_fields(fields),
            forceLatest=force_latest,
        )
        result = self._call_and_maybe_poll("getInstagramUserConnections", args)
        return self._build_paginated_result(
            result, InstagramUser, "getInstagramUserConnections", args
        )

    def get_post_interacting_users(
        self,
        post_id: str,
        interaction_type: str,
        *,
        fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> PaginatedResult[InstagramUser]:
        args = self._build_args(
            postId=post_id,
            interactionType=interaction_type,
            fields=self._convert_fields(fields),
            forceLatest=force_latest,
        )
        result = self._call_and_maybe_poll("getInstagramPostInteractingUsers", args)
        return self._build_paginated_result(
            result, InstagramUser, "getInstagramPostInteractingUsers", args
        )

    def get_users_by_keywords(
        self,
        query: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        force_latest: bool | None = None,
    ) -> PaginatedResult[InstagramUser]:
        args = self._build_args(
            query=query,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            forceLatest=force_latest,
        )
        result = self._call_and_maybe_poll("getInstagramUsersByKeywords", args)
        return self._build_paginated_result(
            result, InstagramUser, "getInstagramUsersByKeywords", args
        )


class AsyncInstagramNamespace(AsyncBaseNamespace):
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
        result = await self._call_and_maybe_poll("getInstagramPostsByIds", args)
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
    ) -> AsyncPaginatedResult[InstagramPost]:
        args = self._build_args(
            identifier=identifier,
            identifierType=identifier_type,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            forceLatest=force_latest,
        )
        result = await self._call_and_maybe_poll("getInstagramPostsByUser", args)
        return await self._build_paginated_result(
            result, InstagramPost, "getInstagramPostsByUser", args
        )

    async def search_posts(
        self,
        query: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        force_latest: bool | None = None,
    ) -> AsyncPaginatedResult[InstagramPost]:
        args = self._build_args(
            query=query,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            forceLatest=force_latest,
        )
        result = await self._call_and_maybe_poll("getInstagramPostsByKeywords", args)
        return await self._build_paginated_result(
            result, InstagramPost, "getInstagramPostsByKeywords", args
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
        result = await self._call_and_maybe_poll("getInstagramCommentsByPostId", args)
        return await self._build_paginated_result(
            result, InstagramComment, "getInstagramCommentsByPostId", args
        )

    async def get_user(
        self,
        identifier: str,
        identifier_type: str = "username",
        *,
        fields: list[str] | None = None,
    ) -> InstagramUser:
        args = self._build_args(
            identifier=identifier,
            identifierType=identifier_type,
            fields=self._convert_fields(fields),
        )
        result = await self._call_and_maybe_poll("getInstagramUser", args)
        results = result.get("results", [])
        if isinstance(results, list) and len(results) > 0:
            return _parse_item(InstagramUser, results[0])
        return _parse_item(InstagramUser, result)

    async def search_users(
        self,
        name: str,
        *,
        limit: int | None = None,
        fields: list[str] | None = None,
    ) -> list[InstagramUser]:
        args = self._build_args(
            name=name,
            limit=limit,
            fields=self._convert_fields(fields),
        )
        result = await self._call_and_maybe_poll("searchInstagramUsers", args)
        return _parse_items(InstagramUser, result.get("results", []))

    async def get_user_connections(
        self,
        username: str,
        connection_type: str,
        *,
        fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> AsyncPaginatedResult[InstagramUser]:
        args = self._build_args(
            username=username,
            connectionType=connection_type,
            fields=self._convert_fields(fields),
            forceLatest=force_latest,
        )
        result = await self._call_and_maybe_poll("getInstagramUserConnections", args)
        return await self._build_paginated_result(
            result, InstagramUser, "getInstagramUserConnections", args
        )

    async def get_post_interacting_users(
        self,
        post_id: str,
        interaction_type: str,
        *,
        fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> AsyncPaginatedResult[InstagramUser]:
        args = self._build_args(
            postId=post_id,
            interactionType=interaction_type,
            fields=self._convert_fields(fields),
            forceLatest=force_latest,
        )
        result = await self._call_and_maybe_poll("getInstagramPostInteractingUsers", args)
        return await self._build_paginated_result(
            result, InstagramUser, "getInstagramPostInteractingUsers", args
        )

    async def get_users_by_keywords(
        self,
        query: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        force_latest: bool | None = None,
    ) -> AsyncPaginatedResult[InstagramUser]:
        args = self._build_args(
            query=query,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            forceLatest=force_latest,
        )
        result = await self._call_and_maybe_poll("getInstagramUsersByKeywords", args)
        return await self._build_paginated_result(
            result, InstagramUser, "getInstagramUsersByKeywords", args
        )
