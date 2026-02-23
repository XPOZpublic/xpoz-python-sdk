from __future__ import annotations

from typing import Any

from pydantic import BaseModel, field_validator


class TwitterPost(BaseModel, extra="allow"):
    id: str | None = None
    text: str | None = None
    author_id: str | None = None
    author_username: str | None = None
    conversation_id: str | None = None
    lang: str | None = None
    source: str | None = None
    status: str | None = None
    deleted: bool | None = None
    suspended: bool | None = None
    possibly_sensitive: bool | None = None
    is_retweet: bool | None = None

    like_count: int | None = None
    retweet_count: int | None = None
    reply_count: int | None = None
    quote_count: int | None = None
    impression_count: int | None = None
    bookmark_count: int | None = None

    quoted_tweet_id: str | None = None
    retweeted_tweet_id: str | None = None
    reply_to_tweet_id: str | None = None
    reply_to_user_id: str | None = None
    reply_to_username: str | None = None
    original_tweet_id: str | None = None
    edited_tweets: list[str] | None = None
    reply_settings: str | None = None

    hashtags: list[str] | None = None
    mentions: list[str] | None = None
    media_urls: list[str] | None = None
    grok_generated_content: list[dict[str, Any]] | None = None
    urls: list[str] | None = None

    country: str | None = None
    region: str | None = None
    city: str | None = None

    has_birdwatch_notes: bool | None = None
    birdwatch_notes_id: str | None = None
    birdwatch_notes_text: str | None = None
    birdwatch_notes_url: str | None = None

    created_at: str | None = None
    created_at_date: str | None = None
    x_fetched_at: str | None = None


class TwitterUser(BaseModel, extra="allow"):
    id: str | None = None
    username: str | None = None

    @field_validator("username", mode="before")
    @classmethod
    def coerce_username(cls, v: Any) -> Any:
        if v is not None and not isinstance(v, str):
            return str(v)
        return v
    name: str | None = None
    description: str | None = None
    location: str | None = None
    verified: bool | None = None
    verified_type: str | None = None
    protected: bool | None = None
    status: str | None = None

    followers_count: int | None = None
    following_count: int | None = None
    tweet_count: int | None = None
    listed_count: int | None = None
    likes_count: int | None = None
    media_count: int | None = None

    profile_image_url: str | None = None
    profile_banner_url: str | None = None
    profile_interstitial_type: str | None = None

    pinned_tweet_id: str | None = None
    source: str | None = None
    is_verified: bool | None = None
    account_based_in: str | None = None
    location_accurate: bool | None = None
    label: str | None = None
    label_type: str | None = None

    collected_following_count: int | None = None
    collected_followers_count: int | None = None
    collected_followers_coverage: float | None = None
    collected_following_coverage: float | None = None
    avg_tweets_per_day_last_month: float | None = None

    n_lang: int | None = None
    n_langs_filtered: int | None = None
    inauthentic_type: str | None = None
    is_inauthentic: bool | None = None
    is_inauthentic_prob_score: float | None = None
    is_inauthentic_calculated_at: str | None = None

    verified_since_datetime: str | None = None
    username_changes: list[str] | None = None
    last_username_change_datetime: str | None = None

    created_at: str | None = None
    created_at_date: str | None = None
    x_fetched_at: str | None = None
    modified_at: str | None = None
    x_modified_at: str | None = None

    agg_relevance: float | None = None
    relevant_tweets_count: int | None = None
    relevant_tweets_impressions_sum: int | None = None
    relevant_tweets_likes_sum: int | None = None
    relevant_tweets_quotes_sum: int | None = None
    relevant_tweets_replies_sum: int | None = None
    relevant_tweets_retweets_sum: int | None = None
