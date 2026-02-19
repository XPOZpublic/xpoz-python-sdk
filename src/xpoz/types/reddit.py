from __future__ import annotations

from pydantic import BaseModel

from xpoz.types.common import PaginationInfo


class RedditPost(BaseModel, extra="allow"):
    id: str | None = None
    title: str | None = None
    selftext: str | None = None
    url: str | None = None
    permalink: str | None = None
    post_url: str | None = None
    thumbnail: str | None = None

    author_id: str | None = None
    author_username: str | None = None

    subreddit_name: str | None = None
    subreddit_id: str | None = None

    score: int | None = None
    upvotes: int | None = None
    downvotes: int | None = None
    upvote_ratio: float | None = None
    comments_count: int | None = None
    crossposts_count: int | None = None

    is_self: bool | None = None
    is_video: bool | None = None
    is_original_content: bool | None = None
    over18: bool | None = None
    spoiler: bool | None = None
    locked: bool | None = None
    stickied: bool | None = None
    archived: bool | None = None

    link_flair_text: str | None = None
    post_hint: str | None = None
    domain: str | None = None
    crosspost_parent: str | None = None

    created_at: str | None = None
    created_at_timestamp: int | None = None
    created_at_date: str | None = None
    last_fetch: str | None = None
    last_fetch_datetime: str | None = None
    x_last_updated: str | None = None


class RedditUser(BaseModel, extra="allow"):
    id: str | None = None
    username: str | None = None
    profile_url: str | None = None
    profile_pic_url: str | None = None
    snoovatar_img: str | None = None

    link_karma: int | None = None
    comment_karma: int | None = None
    total_karma: int | None = None
    awardee_karma: int | None = None
    awarder_karma: int | None = None

    is_gold: bool | None = None
    is_mod: bool | None = None
    is_employee: bool | None = None
    has_verified_email: bool | None = None
    is_suspended: bool | None = None
    verified: bool | None = None
    is_blocked: bool | None = None
    accept_followers: bool | None = None
    has_subscribed: bool | None = None
    hide_from_robots: bool | None = None
    pref_show_snoovatar: bool | None = None

    profile_description: str | None = None
    profile_banner_url: str | None = None
    profile_title: str | None = None

    created_at: str | None = None
    created_at_timestamp: int | None = None
    created_at_date: str | None = None
    last_fetch: str | None = None
    last_fetch_datetime: str | None = None
    x_last_updated: str | None = None

    agg_relevance: float | None = None
    relevant_posts_count: int | None = None
    relevant_posts_upvotes_sum: int | None = None
    relevant_posts_comments_count_sum: int | None = None


class RedditComment(BaseModel, extra="allow"):
    id: str | None = None
    body: str | None = None
    parent_post_id: str | None = None
    parent_id: str | None = None

    author_id: str | None = None
    author_username: str | None = None

    post_subreddit_name: str | None = None
    post_subreddit_id: str | None = None

    score: int | None = None
    upvotes: int | None = None
    downvotes: int | None = None
    controversiality: int | None = None

    depth: int | None = None
    is_submitter: bool | None = None
    stickied: bool | None = None
    collapsed: bool | None = None
    edited: bool | None = None
    distinguished: str | None = None

    created_at: str | None = None
    created_at_timestamp: int | None = None
    created_at_date: str | None = None
    last_fetch: str | None = None
    last_fetch_datetime: str | None = None
    x_last_updated: str | None = None


class RedditSubreddit(BaseModel, extra="allow"):
    id: str | None = None
    display_name: str | None = None
    title: str | None = None
    public_description: str | None = None
    description: str | None = None

    subscribers_count: int | None = None
    active_user_count: int | None = None

    subreddit_type: str | None = None
    over18: bool | None = None
    lang: str | None = None
    url: str | None = None
    subreddit_url: str | None = None

    icon_img: str | None = None
    banner_img: str | None = None
    header_img: str | None = None
    community_icon: str | None = None

    created_at: str | None = None
    created_at_timestamp: int | None = None
    created_at_date: str | None = None
    last_fetch: str | None = None
    last_fetch_datetime: str | None = None
    x_last_updated: str | None = None

    agg_relevance: float | None = None
    relevant_posts_count: int | None = None
    relevant_posts_upvotes_sum: int | None = None
    relevant_posts_comments_count_sum: int | None = None


class RedditPostWithComments(BaseModel):
    post: RedditPost
    comments: list[RedditComment] = []
    comments_pagination: PaginationInfo | None = None
    comments_table_name: str | None = None


class SubredditWithPosts(BaseModel):
    subreddit: RedditSubreddit
    posts: list[RedditPost] = []
    posts_pagination: PaginationInfo | None = None
    posts_table_name: str | None = None
