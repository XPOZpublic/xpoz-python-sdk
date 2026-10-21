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
from xpoz._mcp._polling import wait_for_result_sync, wait_for_result
from xpoz.types.reddit import (
    RedditPost,
    RedditUser,
    RedditComment,
    RedditSubreddit,
    RedditPostWithComments,
    SubredditWithPosts,
)
from xpoz.types.common import PaginationInfo
from xpoz._rest import RestTransport, AsyncRestTransport
from xpoz.namespaces._live_base import _csv_fields, _parse_items as _live_parse_items
from xpoz._config import _routes, _tools
from xpoz._config._constants import ResponseType


class RedditNamespace(BaseNamespace):
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
        response_type: ResponseType | None = None,
        limit: int | None = None,
    ) -> PaginatedResult[RedditPost]:
        if response_type == ResponseType.CSV:
            args = self._build_args(
                query=query, fields=self._convert_fields(fields),
                startDate=start_date, endDate=end_date, sort=sort, time=time,
                subreddit=subreddit, forceLatest=force_latest,
                responseType=response_type, limit=limit,
            )
            result = self._call_and_maybe_poll(_tools.SEARCH_REDDIT_POSTS, args)
            return self._build_paginated_result(result, RedditPost, _tools.SEARCH_REDDIT_POSTS, args)

        params: dict[str, Any] = {
            "q": query, "sort": sort, "time": time, "subreddit": subreddit,
            "since": start_date, "until": end_date, "limit": limit,
            "fields": _csv_fields(fields),
        }
        payload = self._rest.get(_routes.REDDIT_LIVE_POSTS, params)

        def fetch_next(cursor: str) -> dict[str, Any]:
            return self._rest.get(_routes.REDDIT_LIVE_POSTS, {**params, "cursor": cursor})

        return self._cursor_to_paginated_result(RedditPost, payload, fetch_next)

    def get_post_with_comments(
        self,
        post_id: str,
        *,
        post_fields: list[str] | None = None,
        comment_fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> RedditPostWithComments:
        post_payload = self._rest.get(
            _routes.REDDIT_LIVE_POST.format(post_id=post_id),
            {"fields": _csv_fields(post_fields)},
        )
        comments_payload = self._rest.get(
            _routes.REDDIT_LIVE_POST_COMMENTS.format(post_id=post_id),
            {"fields": _csv_fields(comment_fields)},
        )

        post_items = _live_parse_items(RedditPost, post_payload.get("results", []))
        comment_items = _live_parse_items(RedditComment, comments_payload.get("results", []))
        has_more = bool(comments_payload.get("has_more"))

        pagination = PaginationInfo(
            table_name=None, total_rows=0,
            total_pages=2 if has_more else 1, page_number=1,
            page_size=len(comment_items), results_count=len(comment_items),
        )

        return RedditPostWithComments(
            post=post_items[0] if post_items else _parse_item(RedditPost, {}),
            comments=comment_items,
            comments_pagination=pagination if comment_items else None,
            comments_table_name=None,
        )

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

    def get_comment_by_id(
        self,
        comment_id: str,
        *,
        fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> RedditComment:
        args = self._build_args(
            commentId=comment_id,
            fields=self._convert_fields(fields),
            forceLatest=force_latest,
        )
        result = self._call_and_maybe_poll(_tools.GET_REDDIT_COMMENT_BY_ID, args)
        results = result.get("results", [])
        if isinstance(results, list) and len(results) > 0:
            return _parse_item(RedditComment, results[0])
        return _parse_item(RedditComment, result)

    def get_user(
        self,
        username: str,
        *,
        fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> RedditUser:
        payload = self._rest.get(
            _routes.REDDIT_LIVE_USER.format(username=username),
            {"fields": _csv_fields(fields)},
        )
        results = _live_parse_items(RedditUser, payload.get("results", []))
        if results:
            return results[0]
        raise ValueError(f"User not found: {username}")

    def search_users(
        self,
        name: str,
        *,
        limit: int | None = None,
        fields: list[str] | None = None,
    ) -> list[RedditUser]:
        payload = self._rest.get(
            _routes.REDDIT_LIVE_USERS,
            {"q": name, "limit": limit, "fields": _csv_fields(fields)},
        )
        return _live_parse_items(RedditUser, payload.get("results", []))

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
        payload = self._rest.get(
            _routes.REDDIT_LIVE_SUBREDDITS,
            {"q": query, "limit": limit, "fields": _csv_fields(fields)},
        )
        return _live_parse_items(RedditSubreddit, payload.get("results", []))

    def get_subreddit_with_posts(
        self,
        subreddit_name: str,
        *,
        subreddit_fields: list[str] | None = None,
        post_fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> SubredditWithPosts:
        sub_payload = self._rest.get(
            _routes.REDDIT_LIVE_SUBREDDIT.format(name=subreddit_name),
            {"fields": _csv_fields(subreddit_fields)},
        )
        posts_payload = self._rest.get(
            _routes.REDDIT_LIVE_SUBREDDIT_POSTS.format(name=subreddit_name),
            {"fields": _csv_fields(post_fields)},
        )

        sub_items = _live_parse_items(RedditSubreddit, sub_payload.get("results", []))
        post_items = _live_parse_items(RedditPost, posts_payload.get("results", []))
        has_more = bool(posts_payload.get("has_more"))

        pagination = PaginationInfo(
            table_name=None, total_rows=0,
            total_pages=2 if has_more else 1, page_number=1,
            page_size=len(post_items), results_count=len(post_items),
        )

        return SubredditWithPosts(
            subreddit=sub_items[0] if sub_items else _parse_item(RedditSubreddit, {}),
            posts=post_items,
            posts_pagination=pagination if post_items else None,
            posts_table_name=None,
        )

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
        comments_data = results.get("comments") or []
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
        posts_data = results.get("posts") or []
        pagination = _extract_pagination(raw)

        return SubredditWithPosts(
            subreddit=_parse_item(RedditSubreddit, subreddit_data),
            posts=_parse_items(RedditPost, posts_data),
            posts_pagination=pagination if pagination.total_pages > 0 else None,
            posts_table_name=pagination.table_name,
        )


class AsyncRedditNamespace(AsyncBaseNamespace):
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
        response_type: ResponseType | None = None,
        limit: int | None = None,
    ) -> AsyncPaginatedResult[RedditPost]:
        if response_type == ResponseType.CSV:
            args = self._build_args(
                query=query, fields=self._convert_fields(fields),
                startDate=start_date, endDate=end_date, sort=sort, time=time,
                subreddit=subreddit, forceLatest=force_latest,
                responseType=response_type, limit=limit,
            )
            result = await self._call_and_maybe_poll(_tools.SEARCH_REDDIT_POSTS, args)
            return await self._build_paginated_result(result, RedditPost, _tools.SEARCH_REDDIT_POSTS, args)

        params: dict[str, Any] = {
            "q": query, "sort": sort, "time": time, "subreddit": subreddit,
            "since": start_date, "until": end_date, "limit": limit,
            "fields": _csv_fields(fields),
        }
        payload = await self._rest.get(_routes.REDDIT_LIVE_POSTS, params)

        async def fetch_next(cursor: str) -> dict[str, Any]:
            return await self._rest.get(_routes.REDDIT_LIVE_POSTS, {**params, "cursor": cursor})

        return await self._cursor_to_paginated_result(RedditPost, payload, fetch_next)

    async def get_post_with_comments(
        self,
        post_id: str,
        *,
        post_fields: list[str] | None = None,
        comment_fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> RedditPostWithComments:
        import asyncio
        post_payload, comments_payload = await asyncio.gather(
            self._rest.get(
                _routes.REDDIT_LIVE_POST.format(post_id=post_id),
                {"fields": _csv_fields(post_fields)},
            ),
            self._rest.get(
                _routes.REDDIT_LIVE_POST_COMMENTS.format(post_id=post_id),
                {"fields": _csv_fields(comment_fields)},
            ),
        )

        post_items = _live_parse_items(RedditPost, post_payload.get("results", []))
        comment_items = _live_parse_items(RedditComment, comments_payload.get("results", []))
        has_more = bool(comments_payload.get("has_more"))

        pagination = PaginationInfo(
            table_name=None, total_rows=0,
            total_pages=2 if has_more else 1, page_number=1,
            page_size=len(comment_items), results_count=len(comment_items),
        )

        return RedditPostWithComments(
            post=post_items[0] if post_items else _parse_item(RedditPost, {}),
            comments=comment_items,
            comments_pagination=pagination if comment_items else None,
            comments_table_name=None,
        )

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

    async def get_comment_by_id(
        self,
        comment_id: str,
        *,
        fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> RedditComment:
        args = self._build_args(
            commentId=comment_id,
            fields=self._convert_fields(fields),
            forceLatest=force_latest,
        )
        result = await self._call_and_maybe_poll(_tools.GET_REDDIT_COMMENT_BY_ID, args)
        results = result.get("results", [])
        if isinstance(results, list) and len(results) > 0:
            return _parse_item(RedditComment, results[0])
        return _parse_item(RedditComment, result)

    async def get_user(
        self,
        username: str,
        *,
        fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> RedditUser:
        payload = await self._rest.get(
            _routes.REDDIT_LIVE_USER.format(username=username),
            {"fields": _csv_fields(fields)},
        )
        results = _live_parse_items(RedditUser, payload.get("results", []))
        if results:
            return results[0]
        raise ValueError(f"User not found: {username}")

    async def search_users(
        self,
        name: str,
        *,
        limit: int | None = None,
        fields: list[str] | None = None,
    ) -> list[RedditUser]:
        payload = await self._rest.get(
            _routes.REDDIT_LIVE_USERS,
            {"q": name, "limit": limit, "fields": _csv_fields(fields)},
        )
        return _live_parse_items(RedditUser, payload.get("results", []))

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
        payload = await self._rest.get(
            _routes.REDDIT_LIVE_SUBREDDITS,
            {"q": query, "limit": limit, "fields": _csv_fields(fields)},
        )
        return _live_parse_items(RedditSubreddit, payload.get("results", []))

    async def get_subreddit_with_posts(
        self,
        subreddit_name: str,
        *,
        subreddit_fields: list[str] | None = None,
        post_fields: list[str] | None = None,
        force_latest: bool | None = None,
    ) -> SubredditWithPosts:
        import asyncio
        sub_payload, posts_payload = await asyncio.gather(
            self._rest.get(
                _routes.REDDIT_LIVE_SUBREDDIT.format(name=subreddit_name),
                {"fields": _csv_fields(subreddit_fields)},
            ),
            self._rest.get(
                _routes.REDDIT_LIVE_SUBREDDIT_POSTS.format(name=subreddit_name),
                {"fields": _csv_fields(post_fields)},
            ),
        )

        sub_items = _live_parse_items(RedditSubreddit, sub_payload.get("results", []))
        post_items = _live_parse_items(RedditPost, posts_payload.get("results", []))
        has_more = bool(posts_payload.get("has_more"))

        pagination = PaginationInfo(
            table_name=None, total_rows=0,
            total_pages=2 if has_more else 1, page_number=1,
            page_size=len(post_items), results_count=len(post_items),
        )

        return SubredditWithPosts(
            subreddit=sub_items[0] if sub_items else _parse_item(RedditSubreddit, {}),
            posts=post_items,
            posts_pagination=pagination if post_items else None,
            posts_table_name=None,
        )

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
        comments_data = results.get("comments") or []
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
        posts_data = results.get("posts") or []
        pagination = _extract_pagination(raw)

        return SubredditWithPosts(
            subreddit=_parse_item(RedditSubreddit, subreddit_data),
            posts=_parse_items(RedditPost, posts_data),
            posts_pagination=pagination if pagination.total_pages > 0 else None,
            posts_table_name=pagination.table_name,
        )


from xpoz._config import _allowed_fields as _af
from xpoz.namespaces._base import _attach_allowed_fields

_REDDIT_FIELD_METADATA: dict[str, dict[str, frozenset[str]]] = {
    "get_user":                  {"fields": _af.GET_REDDIT_USER_FIELDS},
    "search_users":              {"fields": _af.SEARCH_REDDIT_USERS_FIELDS},
    "get_users_by_keywords":     {"fields": _af.GET_REDDIT_USERS_BY_KEYWORDS_FIELDS},
    "search_posts":              {"fields": _af.SEARCH_REDDIT_POSTS_FIELDS},
    "search_comments":           {"fields": _af.SEARCH_REDDIT_COMMENTS_FIELDS},
    "get_comment_by_id":         {"fields": _af.GET_REDDIT_COMMENT_BY_ID_FIELDS},
    "search_subreddits":         {"fields": _af.SEARCH_REDDIT_SUBREDDITS_FIELDS},
    "get_subreddits_by_keywords": {"fields": _af.GET_REDDIT_SUBREDDITS_BY_KEYWORDS_FIELDS},
    "get_post_with_comments": {
        "post_fields":    _af.GET_REDDIT_POST_WITH_COMMENTS_POST_FIELDS,
        "comment_fields": _af.GET_REDDIT_POST_WITH_COMMENTS_COMMENT_FIELDS,
    },
    "get_subreddit_with_posts": {
        "subreddit_fields": _af.GET_REDDIT_SUBREDDIT_WITH_POSTS_SUBREDDIT_FIELDS,
        "post_fields":      _af.GET_REDDIT_SUBREDDIT_WITH_POSTS_POST_FIELDS,
    },
}

_attach_allowed_fields(RedditNamespace, _REDDIT_FIELD_METADATA)
_attach_allowed_fields(AsyncRedditNamespace, _REDDIT_FIELD_METADATA)
