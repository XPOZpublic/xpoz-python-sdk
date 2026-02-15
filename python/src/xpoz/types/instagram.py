from __future__ import annotations

from pydantic import BaseModel


class InstagramPost(BaseModel, extra="allow"):
    id: str | None = None
    post_type: str | None = None
    user_id: str | None = None
    username: str | None = None
    full_name: str | None = None
    caption: str | None = None
    media_type: str | None = None

    code_url: str | None = None
    image_url: str | None = None
    video_url: str | None = None
    audio_only_url: str | None = None
    profile_pic_url: str | None = None
    video_subtitles_uri: str | None = None

    subtitles: str | None = None
    video_duration: float | None = None

    like_count: int | None = None
    comment_count: int | None = None
    reshare_count: int | None = None
    video_play_count: int | None = None

    location: str | None = None

    created_at: str | None = None
    created_at_timestamp: int | None = None
    created_at_date: str | None = None
    last_fetch: str | None = None
    last_fetch_datetime: str | None = None
    x_last_updated: str | None = None


class InstagramUser(BaseModel, extra="allow"):
    id: str | None = None
    username: str | None = None
    full_name: str | None = None
    biography: str | None = None
    is_private: bool | None = None
    is_verified: bool | None = None

    follower_count: int | None = None
    following_count: int | None = None
    media_count: int | None = None

    profile_pic_url: str | None = None
    profile_pic_id: str | None = None
    profile_url: str | None = None
    external_url: str | None = None
    has_anonymous_profile_picture: bool | None = None

    last_fetch: str | None = None
    last_fetch_datetime: str | None = None
    x_last_updated: str | None = None

    agg_relevance: float | None = None
    relevant_posts_count: int | None = None
    relevant_posts_likes_sum: int | None = None
    relevant_posts_comments_sum: int | None = None
    relevant_posts_reshares_sum: int | None = None
    relevant_posts_video_plays_sum: int | None = None


class InstagramComment(BaseModel, extra="allow"):
    id: str | None = None
    text: str | None = None
    parent_post_id: str | None = None
    parent_post_user_id: str | None = None
    type: str | None = None
    parent_comment_id: str | None = None
    replied_to_comment_id: str | None = None
    child_comment_count: int | None = None

    user_id: str | None = None
    username: str | None = None
    full_name: str | None = None

    like_count: int | None = None
    status: str | None = None
    is_spam: bool | None = None
    has_translation: bool | None = None

    created_at: str | None = None
    created_at_timestamp: int | None = None
    created_at_date: str | None = None
    last_fetch: str | None = None
    last_fetch_datetime: str | None = None
    x_last_updated: str | None = None
