from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class TrackedItem(BaseModel, extra="allow"):
    phrase: str | None = None
    type: Literal["keyword", "user", "subreddit"] | None = None
    platform: Literal["twitter", "instagram", "reddit", "tiktok"] | None = None


class AddTrackedItemsResult(BaseModel, extra="allow"):
    success: bool | None = None
    added_count: int | None = None
    message: str | None = None
    current_count: int | None = None
    max_tracked_items: int | None = None
    plan_name: str | None = None


class RemoveTrackedItemsResult(BaseModel, extra="allow"):
    success: bool | None = None
    removed_count: int | None = None
    message: str | None = None
