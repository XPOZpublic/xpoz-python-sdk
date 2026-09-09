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
from xpoz.types.instagram import InstagramComment, InstagramPost, InstagramUser

INTERACTION_COMMENTERS = "commenters"
INTERACTION_LIKERS = "likers"

__all__ = [
    "AsyncInstagramLiveNamespace",
    "CONNECTION_FOLLOWERS",
    "CONNECTION_FOLLOWING",
    "INTERACTION_COMMENTERS",
    "INTERACTION_LIKERS",
    "InstagramLiveNamespace",
]


class InstagramLiveNamespace(LiveNamespace):
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


class AsyncInstagramLiveNamespace(AsyncLiveNamespace):
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
