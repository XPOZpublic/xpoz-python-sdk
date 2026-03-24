from __future__ import annotations

from pydantic import BaseModel


class TiktokPost(BaseModel, extra="allow"):
    id: str | None = None
    post_type: int | None = None
    is_private: bool | None = None
    video_thumbnail: str | None = None
    description: str | None = None
    description_language: str | None = None

    user_id: str | None = None
    username: str | None = None
    nickname: str | None = None

    collect_count: int | None = None
    comment_count: int | None = None
    like_count: int | None = None
    download_count: int | None = None
    forward_count: int | None = None
    play_count: int | None = None

    created_at: str | None = None
    created_at_timestamp: int | None = None
    created_at_date: str | None = None
    last_fetch: str | None = None
    last_fetch_datetime: str | None = None
    x_last_updated: str | None = None

    agg_relevance: float | None = None
    relevant_posts_count: int | None = None
    relevant_posts_likes_sum: int | None = None
    relevant_posts_comments_sum: int | None = None
    relevant_posts_plays_sum: int | None = None
    relevant_posts_forwards_sum: int | None = None


class TiktokUser(BaseModel, extra="allow"):
    id: str | None = None
    username: str | None = None
    nickname: str | None = None
    signature: str | None = None
    sec_uid: str | None = None
    avatar: str | None = None

    is_private: bool | None = None
    is_verified: bool | None = None

    follower_count: int | None = None
    following_count: int | None = None
    like_count: int | None = None
    post_count: int | None = None

    language: str | None = None
    region: str | None = None

    created_at: str | None = None
    username_modify_time: str | None = None
    last_fetch: str | None = None
    last_fetch_datetime: str | None = None
    x_last_updated: str | None = None

    agg_relevance: float | None = None
    relevant_posts_count: int | None = None
    relevant_posts_likes_sum: int | None = None
    relevant_posts_comments_sum: int | None = None
    relevant_posts_plays_sum: int | None = None
    relevant_posts_forwards_sum: int | None = None


class TiktokComment(BaseModel, extra="allow"):
    id: str | None = None
    post_id: str | None = None
    user_id: str | None = None
    username: str | None = None
    text: str | None = None

    like_count: int | None = None

    created_at: str | None = None
    created_at_timestamp: int | None = None
    created_at_date: str | None = None
    last_fetch: str | None = None
    last_fetch_datetime: str | None = None
    x_last_updated: str | None = None
