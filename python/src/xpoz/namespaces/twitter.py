from __future__ import annotations

from typing import Any

from xpoz.namespaces._base import BaseNamespace, AsyncBaseNamespace, _parse_item, _parse_items
from xpoz._pagination import PaginatedResult, AsyncPaginatedResult
from xpoz.types.twitter import Tweet, TwitterUser


class TwitterNamespace(BaseNamespace):
    def get_posts_by_ids(
        self,
        post_ids: list[str],
        *,
        fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> list[Tweet]:
        args = self._build_args(
            postIds=post_ids,
            fields=self._convert_fields(fields),
            forceLatest=force_latest,
        )
        result = self._call_and_maybe_poll("getTwitterPostsByIds", args)
        return _parse_items(Tweet, result.get("results", []))

    def get_posts_by_author(
        self,
        identifier: str,
        identifier_type: str = "username",
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        force_latest: bool | None = None,
    ) -> PaginatedResult[Tweet]:
        args = self._build_args(
            identifier=identifier,
            identifierType=identifier_type,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            forceLatest=force_latest,
        )
        result = self._call_and_maybe_poll("getTwitterPostsByAuthor", args)
        return self._build_paginated_result(result, Tweet, "getTwitterPostsByAuthor", args)

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
        force_latest: bool | None = None,
    ) -> PaginatedResult[Tweet]:
        args = self._build_args(
            query=query,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            authorUsername=author_username,
            authorId=author_id,
            language=language,
            forceLatest=force_latest,
        )
        result = self._call_and_maybe_poll("getTwitterPostsByKeywords", args)
        return self._build_paginated_result(result, Tweet, "getTwitterPostsByKeywords", args)

    def get_retweets(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
    ) -> PaginatedResult[Tweet]:
        args = self._build_args(
            postId=post_id,
            fields=self._convert_fields(fields),
            startDate=start_date,
        )
        result = self._call_and_maybe_poll("getTwitterPostRetweets", args)
        return self._build_paginated_result(result, Tweet, "getTwitterPostRetweets", args)

    def get_quotes(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        force_latest: bool | None = None,
    ) -> PaginatedResult[Tweet]:
        args = self._build_args(
            postId=post_id,
            fields=self._convert_fields(fields),
            startDate=start_date,
            forceLatest=force_latest,
        )
        result = self._call_and_maybe_poll("getTwitterPostQuotes", args)
        return self._build_paginated_result(result, Tweet, "getTwitterPostQuotes", args)

    def get_comments(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        force_latest: bool | None = None,
    ) -> PaginatedResult[Tweet]:
        args = self._build_args(
            postId=post_id,
            fields=self._convert_fields(fields),
            startDate=start_date,
            forceLatest=force_latest,
        )
        result = self._call_and_maybe_poll("getTwitterPostComments", args)
        return self._build_paginated_result(result, Tweet, "getTwitterPostComments", args)

    def get_post_interacting_users(
        self,
        post_id: str,
        interaction_type: str,
        *,
        fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> PaginatedResult[TwitterUser]:
        args = self._build_args(
            postId=post_id,
            interactionType=interaction_type,
            fields=self._convert_fields(fields),
            forceLatest=force_latest,
        )
        result = self._call_and_maybe_poll("getTwitterPostInteractingUsers", args)
        return self._build_paginated_result(
            result, TwitterUser, "getTwitterPostInteractingUsers", args
        )

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
        result = self._call_and_maybe_poll("countTweets", args)
        count = result.get("results", result.get("count", 0))
        if isinstance(count, list) and len(count) > 0:
            first = count[0]
            if isinstance(first, dict):
                return int(next(iter(first.values())))
            return int(first)
        return int(count)

    def get_user(
        self,
        identifier: str,
        identifier_type: str = "username",
        *,
        fields: list[str] | None = None,
    ) -> TwitterUser:
        args = self._build_args(
            identifier=identifier,
            identifierType=identifier_type,
            fields=self._convert_fields(fields),
        )
        result = self._call_and_maybe_poll("getTwitterUser", args)
        results = result.get("results", [])
        if isinstance(results, list) and len(results) > 0:
            return _parse_item(TwitterUser, results[0])
        return _parse_item(TwitterUser, result)

    def search_users(
        self,
        name: str,
        *,
        limit: int | None = None,
        fields: list[str] | None = None,
    ) -> list[TwitterUser]:
        args = self._build_args(
            name=name,
            limit=limit,
            fields=self._convert_fields(fields),
        )
        result = self._call_and_maybe_poll("searchTwitterUsers", args)
        return _parse_items(TwitterUser, result.get("results", []))

    def get_user_connections(
        self,
        username: str,
        connection_type: str,
        *,
        fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> PaginatedResult[TwitterUser]:
        args = self._build_args(
            username=username,
            connectionType=connection_type,
            fields=self._convert_fields(fields),
            forceLatest=force_latest,
        )
        result = self._call_and_maybe_poll("getTwitterUserConnections", args)
        return self._build_paginated_result(
            result, TwitterUser, "getTwitterUserConnections", args
        )

    def get_users_by_keywords(
        self,
        query: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        language: str | None = None,
        force_latest: bool | None = None,
    ) -> PaginatedResult[TwitterUser]:
        args = self._build_args(
            query=query,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            language=language,
            forceLatest=force_latest,
        )
        result = self._call_and_maybe_poll("getTwitterUsersByKeywords", args)
        return self._build_paginated_result(
            result, TwitterUser, "getTwitterUsersByKeywords", args
        )


class AsyncTwitterNamespace(AsyncBaseNamespace):
    async def get_posts_by_ids(
        self,
        post_ids: list[str],
        *,
        fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> list[Tweet]:
        args = self._build_args(
            postIds=post_ids,
            fields=self._convert_fields(fields),
            forceLatest=force_latest,
        )
        result = await self._call_and_maybe_poll("getTwitterPostsByIds", args)
        return _parse_items(Tweet, result.get("results", []))

    async def get_posts_by_author(
        self,
        identifier: str,
        identifier_type: str = "username",
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        force_latest: bool | None = None,
    ) -> AsyncPaginatedResult[Tweet]:
        args = self._build_args(
            identifier=identifier,
            identifierType=identifier_type,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            forceLatest=force_latest,
        )
        result = await self._call_and_maybe_poll("getTwitterPostsByAuthor", args)
        return await self._build_paginated_result(
            result, Tweet, "getTwitterPostsByAuthor", args
        )

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
        force_latest: bool | None = None,
    ) -> AsyncPaginatedResult[Tweet]:
        args = self._build_args(
            query=query,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            authorUsername=author_username,
            authorId=author_id,
            language=language,
            forceLatest=force_latest,
        )
        result = await self._call_and_maybe_poll("getTwitterPostsByKeywords", args)
        return await self._build_paginated_result(
            result, Tweet, "getTwitterPostsByKeywords", args
        )

    async def get_retweets(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
    ) -> AsyncPaginatedResult[Tweet]:
        args = self._build_args(
            postId=post_id,
            fields=self._convert_fields(fields),
            startDate=start_date,
        )
        result = await self._call_and_maybe_poll("getTwitterPostRetweets", args)
        return await self._build_paginated_result(
            result, Tweet, "getTwitterPostRetweets", args
        )

    async def get_quotes(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        force_latest: bool | None = None,
    ) -> AsyncPaginatedResult[Tweet]:
        args = self._build_args(
            postId=post_id,
            fields=self._convert_fields(fields),
            startDate=start_date,
            forceLatest=force_latest,
        )
        result = await self._call_and_maybe_poll("getTwitterPostQuotes", args)
        return await self._build_paginated_result(
            result, Tweet, "getTwitterPostQuotes", args
        )

    async def get_comments(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        force_latest: bool | None = None,
    ) -> AsyncPaginatedResult[Tweet]:
        args = self._build_args(
            postId=post_id,
            fields=self._convert_fields(fields),
            startDate=start_date,
            forceLatest=force_latest,
        )
        result = await self._call_and_maybe_poll("getTwitterPostComments", args)
        return await self._build_paginated_result(
            result, Tweet, "getTwitterPostComments", args
        )

    async def get_post_interacting_users(
        self,
        post_id: str,
        interaction_type: str,
        *,
        fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> AsyncPaginatedResult[TwitterUser]:
        args = self._build_args(
            postId=post_id,
            interactionType=interaction_type,
            fields=self._convert_fields(fields),
            forceLatest=force_latest,
        )
        result = await self._call_and_maybe_poll("getTwitterPostInteractingUsers", args)
        return await self._build_paginated_result(
            result, TwitterUser, "getTwitterPostInteractingUsers", args
        )

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
        result = await self._call_and_maybe_poll("countTweets", args)
        count = result.get("results", result.get("count", 0))
        if isinstance(count, list) and len(count) > 0:
            first = count[0]
            if isinstance(first, dict):
                return int(next(iter(first.values())))
            return int(first)
        return int(count)

    async def get_user(
        self,
        identifier: str,
        identifier_type: str = "username",
        *,
        fields: list[str] | None = None,
    ) -> TwitterUser:
        args = self._build_args(
            identifier=identifier,
            identifierType=identifier_type,
            fields=self._convert_fields(fields),
        )
        result = await self._call_and_maybe_poll("getTwitterUser", args)
        results = result.get("results", [])
        if isinstance(results, list) and len(results) > 0:
            return _parse_item(TwitterUser, results[0])
        return _parse_item(TwitterUser, result)

    async def search_users(
        self,
        name: str,
        *,
        limit: int | None = None,
        fields: list[str] | None = None,
    ) -> list[TwitterUser]:
        args = self._build_args(
            name=name,
            limit=limit,
            fields=self._convert_fields(fields),
        )
        result = await self._call_and_maybe_poll("searchTwitterUsers", args)
        return _parse_items(TwitterUser, result.get("results", []))

    async def get_user_connections(
        self,
        username: str,
        connection_type: str,
        *,
        fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> AsyncPaginatedResult[TwitterUser]:
        args = self._build_args(
            username=username,
            connectionType=connection_type,
            fields=self._convert_fields(fields),
            forceLatest=force_latest,
        )
        result = await self._call_and_maybe_poll("getTwitterUserConnections", args)
        return await self._build_paginated_result(
            result, TwitterUser, "getTwitterUserConnections", args
        )

    async def get_users_by_keywords(
        self,
        query: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        language: str | None = None,
        force_latest: bool | None = None,
    ) -> AsyncPaginatedResult[TwitterUser]:
        args = self._build_args(
            query=query,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            language=language,
            forceLatest=force_latest,
        )
        result = await self._call_and_maybe_poll("getTwitterUsersByKeywords", args)
        return await self._build_paginated_result(
            result, TwitterUser, "getTwitterUsersByKeywords", args
        )
