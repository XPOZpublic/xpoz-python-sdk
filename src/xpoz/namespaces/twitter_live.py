from __future__ import annotations

from xpoz._config import _routes
from xpoz._cursor import AsyncCursorResult, CursorResult
from xpoz.namespaces._live_base import (
    CONNECTION_FOLLOWERS,
    CONNECTION_FOLLOWING,
    AsyncLiveNamespace,
    LiveNamespace,
    _csv_fields,
)
from xpoz.types.twitter import TwitterPost, TwitterUser

INTERACTION_COMMENTERS = "commenters"
INTERACTION_QUOTERS = "quoters"
INTERACTION_RETWEETERS = "retweeters"
SORT_BY_RELEVANCE = "relevance"
SORT_BY_LATEST = "latest"

__all__ = [
    "AsyncTwitterLiveNamespace",
    "CONNECTION_FOLLOWERS",
    "CONNECTION_FOLLOWING",
    "INTERACTION_COMMENTERS",
    "INTERACTION_QUOTERS",
    "INTERACTION_RETWEETERS",
    "SORT_BY_LATEST",
    "SORT_BY_RELEVANCE",
    "TwitterLiveNamespace",
]


class TwitterLiveNamespace(LiveNamespace):
    def search_posts(
        self,
        query: str,
        *,
        since: str | None = None,
        until: str | None = None,
        lang: str | None = None,
        country_code: str | None = None,
        sort_by: str | None = None,
        fields: list[str] | None = None,
        cursor: str | None = None,
    ) -> CursorResult[TwitterPost]:
        return self._page(
            TwitterPost,
            _routes.TWITTER_LIVE_POSTS,
            {
                "q": query,
                "since": since,
                "until": until,
                "lang": lang,
                "countryCode": country_code,
                "sortBy": sort_by,
                "fields": _csv_fields(fields),
                "cursor": cursor,
            },
        )

    def get_posts_by_user(
        self,
        username: str,
        *,
        since: str | None = None,
        until: str | None = None,
        fields: list[str] | None = None,
        cursor: str | None = None,
    ) -> CursorResult[TwitterPost]:
        return self._page(
            TwitterPost,
            _routes.TWITTER_LIVE_USER_POSTS.format(username=username),
            {
                "since": since,
                "until": until,
                "fields": _csv_fields(fields),
                "cursor": cursor,
            },
        )

    def get_post(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
    ) -> TwitterPost | None:
        return self._single(
            TwitterPost,
            _routes.TWITTER_LIVE_POST.format(post_id=post_id),
            {"fields": _csv_fields(fields)},
        )

    def get_comments(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
        cursor: str | None = None,
    ) -> CursorResult[TwitterPost]:
        return self._page(
            TwitterPost,
            _routes.TWITTER_LIVE_POST_COMMENTS.format(post_id=post_id),
            {"fields": _csv_fields(fields), "cursor": cursor},
        )

    def get_quotes(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
        cursor: str | None = None,
    ) -> CursorResult[TwitterPost]:
        return self._page(
            TwitterPost,
            _routes.TWITTER_LIVE_POST_QUOTES.format(post_id=post_id),
            {"fields": _csv_fields(fields), "cursor": cursor},
        )

    def get_post_interacting_users(
        self,
        post_id: str,
        interaction_type: str,
        *,
        fields: list[str] | None = None,
        cursor: str | None = None,
    ) -> CursorResult[TwitterUser]:
        return self._page(
            TwitterUser,
            _routes.TWITTER_LIVE_POST_INTERACTING_USERS.format(post_id=post_id),
            {
                "interactionType": interaction_type,
                "fields": _csv_fields(fields),
                "cursor": cursor,
            },
        )

    def search_users(
        self,
        query: str,
        *,
        fields: list[str] | None = None,
        cursor: str | None = None,
    ) -> CursorResult[TwitterUser]:
        return self._page(
            TwitterUser,
            _routes.TWITTER_LIVE_USERS,
            {"q": query, "fields": _csv_fields(fields), "cursor": cursor},
        )

    def get_user(
        self,
        username: str,
        *,
        fields: list[str] | None = None,
    ) -> TwitterUser | None:
        return self._single(
            TwitterUser,
            _routes.TWITTER_LIVE_USER.format(username=username),
            {"fields": _csv_fields(fields)},
        )

    def get_user_connections(
        self,
        username: str,
        connection_type: str,
        *,
        fields: list[str] | None = None,
        cursor: str | None = None,
    ) -> CursorResult[TwitterUser]:
        return self._page(
            TwitterUser,
            _routes.TWITTER_LIVE_USER_CONNECTIONS.format(username=username),
            {
                "connectionType": connection_type,
                "fields": _csv_fields(fields),
                "cursor": cursor,
            },
        )


class AsyncTwitterLiveNamespace(AsyncLiveNamespace):
    async def search_posts(
        self,
        query: str,
        *,
        since: str | None = None,
        until: str | None = None,
        lang: str | None = None,
        country_code: str | None = None,
        sort_by: str | None = None,
        fields: list[str] | None = None,
        cursor: str | None = None,
    ) -> AsyncCursorResult[TwitterPost]:
        return await self._page(
            TwitterPost,
            _routes.TWITTER_LIVE_POSTS,
            {
                "q": query,
                "since": since,
                "until": until,
                "lang": lang,
                "countryCode": country_code,
                "sortBy": sort_by,
                "fields": _csv_fields(fields),
                "cursor": cursor,
            },
        )

    async def get_posts_by_user(
        self,
        username: str,
        *,
        since: str | None = None,
        until: str | None = None,
        fields: list[str] | None = None,
        cursor: str | None = None,
    ) -> AsyncCursorResult[TwitterPost]:
        return await self._page(
            TwitterPost,
            _routes.TWITTER_LIVE_USER_POSTS.format(username=username),
            {
                "since": since,
                "until": until,
                "fields": _csv_fields(fields),
                "cursor": cursor,
            },
        )

    async def get_post(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
    ) -> TwitterPost | None:
        return await self._single(
            TwitterPost,
            _routes.TWITTER_LIVE_POST.format(post_id=post_id),
            {"fields": _csv_fields(fields)},
        )

    async def get_comments(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
        cursor: str | None = None,
    ) -> AsyncCursorResult[TwitterPost]:
        return await self._page(
            TwitterPost,
            _routes.TWITTER_LIVE_POST_COMMENTS.format(post_id=post_id),
            {"fields": _csv_fields(fields), "cursor": cursor},
        )

    async def get_quotes(
        self,
        post_id: str,
        *,
        fields: list[str] | None = None,
        cursor: str | None = None,
    ) -> AsyncCursorResult[TwitterPost]:
        return await self._page(
            TwitterPost,
            _routes.TWITTER_LIVE_POST_QUOTES.format(post_id=post_id),
            {"fields": _csv_fields(fields), "cursor": cursor},
        )

    async def get_post_interacting_users(
        self,
        post_id: str,
        interaction_type: str,
        *,
        fields: list[str] | None = None,
        cursor: str | None = None,
    ) -> AsyncCursorResult[TwitterUser]:
        return await self._page(
            TwitterUser,
            _routes.TWITTER_LIVE_POST_INTERACTING_USERS.format(post_id=post_id),
            {
                "interactionType": interaction_type,
                "fields": _csv_fields(fields),
                "cursor": cursor,
            },
        )

    async def search_users(
        self,
        query: str,
        *,
        fields: list[str] | None = None,
        cursor: str | None = None,
    ) -> AsyncCursorResult[TwitterUser]:
        return await self._page(
            TwitterUser,
            _routes.TWITTER_LIVE_USERS,
            {"q": query, "fields": _csv_fields(fields), "cursor": cursor},
        )

    async def get_user(
        self,
        username: str,
        *,
        fields: list[str] | None = None,
    ) -> TwitterUser | None:
        return await self._single(
            TwitterUser,
            _routes.TWITTER_LIVE_USER.format(username=username),
            {"fields": _csv_fields(fields)},
        )

    async def get_user_connections(
        self,
        username: str,
        connection_type: str,
        *,
        fields: list[str] | None = None,
        cursor: str | None = None,
    ) -> AsyncCursorResult[TwitterUser]:
        return await self._page(
            TwitterUser,
            _routes.TWITTER_LIVE_USER_CONNECTIONS.format(username=username),
            {
                "connectionType": connection_type,
                "fields": _csv_fields(fields),
                "cursor": cursor,
            },
        )
