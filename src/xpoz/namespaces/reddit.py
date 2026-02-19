from __future__ import annotations

from typing import Any

from xpoz.namespaces._base import (
    BaseNamespace,
    AsyncBaseNamespace,
    _parse_item,
    _parse_items,
    _extract_pagination,
    _extract_results,
)
from xpoz._pagination import PaginatedResult, AsyncPaginatedResult
from xpoz._polling import wait_for_result_sync, wait_for_result
from xpoz.types.reddit import (
    RedditPost,
    RedditUser,
    RedditComment,
    RedditSubreddit,
    RedditPostWithComments,
    SubredditWithPosts,
)
from xpoz.types.common import PaginationInfo
from xpoz import _tools


class RedditNamespace(BaseNamespace):
    def search_posts(
        self,
        query: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        sort: str | None = None,
        time: str | None = None,
        subreddit: str | None = None,
        force_latest: bool | None = None,
    ) -> PaginatedResult[RedditPost]:
        args = self._build_args(
            query=query,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            sort=sort,
            time=time,
            subreddit=subreddit,
            forceLatest=force_latest,
        )
        result = self._call_and_maybe_poll(_tools.SEARCH_REDDIT_POSTS, args)
        return self._build_paginated_result(
            result, RedditPost, _tools.SEARCH_REDDIT_POSTS, args
        )

    def get_post_with_comments(
        self,
        post_id: str,
        *,
        post_fields: list[str] | None = None,
        comment_fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> RedditPostWithComments:
        args = self._build_args(
            postId=post_id,
            postFields=self._convert_fields(post_fields),
            commentFields=self._convert_fields(comment_fields),
            forceLatest=force_latest,
        )
        result = self._call_and_maybe_poll(_tools.GET_REDDIT_POST_WITH_COMMENTS, args)
        return self._parse_post_with_comments(result)

    def search_comments(
        self,
        query: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        subreddit: str | None = None,
    ) -> PaginatedResult[RedditComment]:
        args = self._build_args(
            query=query,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            subreddit=subreddit,
        )
        result = self._call_and_maybe_poll(_tools.SEARCH_REDDIT_COMMENTS, args)
        return self._build_paginated_result(
            result, RedditComment, _tools.SEARCH_REDDIT_COMMENTS, args
        )

    def get_user(
        self,
        username: str,
        *,
        fields: list[str] | None = None,
    ) -> RedditUser:
        args = self._build_args(
            username=username,
            fields=self._convert_fields(fields),
        )
        result = self._call_and_maybe_poll(_tools.GET_REDDIT_USER, args)
        results = result.get("results", [])
        if isinstance(results, list) and len(results) > 0:
            return _parse_item(RedditUser, results[0])
        return _parse_item(RedditUser, result)

    def search_users(
        self,
        name: str,
        *,
        limit: int | None = None,
        fields: list[str] | None = None,
    ) -> list[RedditUser]:
        args = self._build_args(
            name=name,
            limit=limit,
            fields=self._convert_fields(fields),
        )
        result = self._call_and_maybe_poll(_tools.SEARCH_REDDIT_USERS, args)
        return _parse_items(RedditUser, result.get("results", []))

    def get_users_by_keywords(
        self,
        query: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        subreddit: str | None = None,
        force_latest: bool | None = None,
    ) -> PaginatedResult[RedditUser]:
        args = self._build_args(
            query=query,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            subreddit=subreddit,
            forceLatest=force_latest,
        )
        result = self._call_and_maybe_poll(_tools.GET_REDDIT_USERS_BY_KEYWORDS, args)
        return self._build_paginated_result(
            result, RedditUser, _tools.GET_REDDIT_USERS_BY_KEYWORDS, args
        )

    def search_subreddits(
        self,
        query: str,
        *,
        limit: int | None = None,
        fields: list[str] | None = None,
    ) -> list[RedditSubreddit]:
        args = self._build_args(
            query=query,
            limit=limit,
            fields=self._convert_fields(fields),
        )
        result = self._call_and_maybe_poll(_tools.SEARCH_REDDIT_SUBREDDITS, args)
        return _parse_items(RedditSubreddit, result.get("results", []))

    def get_subreddit_with_posts(
        self,
        subreddit_name: str,
        *,
        subreddit_fields: list[str] | None = None,
        post_fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> SubredditWithPosts:
        args = self._build_args(
            subredditName=subreddit_name,
            subredditFields=self._convert_fields(subreddit_fields),
            postFields=self._convert_fields(post_fields),
            forceLatest=force_latest,
        )
        result = self._call_and_maybe_poll(_tools.GET_REDDIT_SUBREDDIT_WITH_POSTS, args)
        return self._parse_subreddit_with_posts(result)

    def get_subreddits_by_keywords(
        self,
        query: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        force_latest: bool | None = None,
    ) -> PaginatedResult[RedditSubreddit]:
        args = self._build_args(
            query=query,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            forceLatest=force_latest,
        )
        result = self._call_and_maybe_poll(_tools.GET_REDDIT_SUBREDDITS_BY_KEYWORDS, args)
        return self._build_paginated_result(
            result, RedditSubreddit, _tools.GET_REDDIT_SUBREDDITS_BY_KEYWORDS, args
        )

    def _parse_post_with_comments(self, raw: dict[str, Any]) -> RedditPostWithComments:
        results = raw.get("results", {})
        if isinstance(results, list):
            results = results[0] if results else {}

        post_data = results.get("post", results)
        comments_data = results.get("comments", [])
        pagination = _extract_pagination(raw)

        return RedditPostWithComments(
            post=_parse_item(RedditPost, post_data),
            comments=_parse_items(RedditComment, comments_data),
            comments_pagination=pagination if pagination.total_pages > 0 else None,
            comments_table_name=pagination.table_name,
        )

    def _parse_subreddit_with_posts(self, raw: dict[str, Any]) -> SubredditWithPosts:
        results = raw.get("results", {})
        if isinstance(results, list):
            results = results[0] if results else {}

        subreddit_data = results.get("subreddit", results)
        posts_data = results.get("posts", [])
        pagination = _extract_pagination(raw)

        return SubredditWithPosts(
            subreddit=_parse_item(RedditSubreddit, subreddit_data),
            posts=_parse_items(RedditPost, posts_data),
            posts_pagination=pagination if pagination.total_pages > 0 else None,
            posts_table_name=pagination.table_name,
        )


class AsyncRedditNamespace(AsyncBaseNamespace):
    async def search_posts(
        self,
        query: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        sort: str | None = None,
        time: str | None = None,
        subreddit: str | None = None,
        force_latest: bool | None = None,
    ) -> AsyncPaginatedResult[RedditPost]:
        args = self._build_args(
            query=query,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            sort=sort,
            time=time,
            subreddit=subreddit,
            forceLatest=force_latest,
        )
        result = await self._call_and_maybe_poll(_tools.SEARCH_REDDIT_POSTS, args)
        return await self._build_paginated_result(
            result, RedditPost, _tools.SEARCH_REDDIT_POSTS, args
        )

    async def get_post_with_comments(
        self,
        post_id: str,
        *,
        post_fields: list[str] | None = None,
        comment_fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> RedditPostWithComments:
        args = self._build_args(
            postId=post_id,
            postFields=self._convert_fields(post_fields),
            commentFields=self._convert_fields(comment_fields),
            forceLatest=force_latest,
        )
        result = await self._call_and_maybe_poll(_tools.GET_REDDIT_POST_WITH_COMMENTS, args)
        return self._parse_post_with_comments(result)

    async def search_comments(
        self,
        query: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        subreddit: str | None = None,
    ) -> AsyncPaginatedResult[RedditComment]:
        args = self._build_args(
            query=query,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            subreddit=subreddit,
        )
        result = await self._call_and_maybe_poll(_tools.SEARCH_REDDIT_COMMENTS, args)
        return await self._build_paginated_result(
            result, RedditComment, _tools.SEARCH_REDDIT_COMMENTS, args
        )

    async def get_user(
        self,
        username: str,
        *,
        fields: list[str] | None = None,
    ) -> RedditUser:
        args = self._build_args(
            username=username,
            fields=self._convert_fields(fields),
        )
        result = await self._call_and_maybe_poll(_tools.GET_REDDIT_USER, args)
        results = result.get("results", [])
        if isinstance(results, list) and len(results) > 0:
            return _parse_item(RedditUser, results[0])
        return _parse_item(RedditUser, result)

    async def search_users(
        self,
        name: str,
        *,
        limit: int | None = None,
        fields: list[str] | None = None,
    ) -> list[RedditUser]:
        args = self._build_args(
            name=name,
            limit=limit,
            fields=self._convert_fields(fields),
        )
        result = await self._call_and_maybe_poll(_tools.SEARCH_REDDIT_USERS, args)
        return _parse_items(RedditUser, result.get("results", []))

    async def get_users_by_keywords(
        self,
        query: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        subreddit: str | None = None,
        force_latest: bool | None = None,
    ) -> AsyncPaginatedResult[RedditUser]:
        args = self._build_args(
            query=query,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            subreddit=subreddit,
            forceLatest=force_latest,
        )
        result = await self._call_and_maybe_poll(_tools.GET_REDDIT_USERS_BY_KEYWORDS, args)
        return await self._build_paginated_result(
            result, RedditUser, _tools.GET_REDDIT_USERS_BY_KEYWORDS, args
        )

    async def search_subreddits(
        self,
        query: str,
        *,
        limit: int | None = None,
        fields: list[str] | None = None,
    ) -> list[RedditSubreddit]:
        args = self._build_args(
            query=query,
            limit=limit,
            fields=self._convert_fields(fields),
        )
        result = await self._call_and_maybe_poll(_tools.SEARCH_REDDIT_SUBREDDITS, args)
        return _parse_items(RedditSubreddit, result.get("results", []))

    async def get_subreddit_with_posts(
        self,
        subreddit_name: str,
        *,
        subreddit_fields: list[str] | None = None,
        post_fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> SubredditWithPosts:
        args = self._build_args(
            subredditName=subreddit_name,
            subredditFields=self._convert_fields(subreddit_fields),
            postFields=self._convert_fields(post_fields),
            forceLatest=force_latest,
        )
        result = await self._call_and_maybe_poll(_tools.GET_REDDIT_SUBREDDIT_WITH_POSTS, args)
        return self._parse_subreddit_with_posts(result)

    async def get_subreddits_by_keywords(
        self,
        query: str,
        *,
        fields: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        force_latest: bool | None = None,
    ) -> AsyncPaginatedResult[RedditSubreddit]:
        args = self._build_args(
            query=query,
            fields=self._convert_fields(fields),
            startDate=start_date,
            endDate=end_date,
            forceLatest=force_latest,
        )
        result = await self._call_and_maybe_poll(_tools.GET_REDDIT_SUBREDDITS_BY_KEYWORDS, args)
        return await self._build_paginated_result(
            result, RedditSubreddit, _tools.GET_REDDIT_SUBREDDITS_BY_KEYWORDS, args
        )

    def _parse_post_with_comments(self, raw: dict[str, Any]) -> RedditPostWithComments:
        results = raw.get("results", {})
        if isinstance(results, list):
            results = results[0] if results else {}

        post_data = results.get("post", results)
        comments_data = results.get("comments", [])
        pagination = _extract_pagination(raw)

        return RedditPostWithComments(
            post=_parse_item(RedditPost, post_data),
            comments=_parse_items(RedditComment, comments_data),
            comments_pagination=pagination if pagination.total_pages > 0 else None,
            comments_table_name=pagination.table_name,
        )

    def _parse_subreddit_with_posts(self, raw: dict[str, Any]) -> SubredditWithPosts:
        results = raw.get("results", {})
        if isinstance(results, list):
            results = results[0] if results else {}

        subreddit_data = results.get("subreddit", results)
        posts_data = results.get("posts", [])
        pagination = _extract_pagination(raw)

        return SubredditWithPosts(
            subreddit=_parse_item(RedditSubreddit, subreddit_data),
            posts=_parse_items(RedditPost, posts_data),
            posts_pagination=pagination if pagination.total_pages > 0 else None,
            posts_table_name=pagination.table_name,
        )
