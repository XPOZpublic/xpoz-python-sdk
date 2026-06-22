from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class PlanFeatures(BaseModel, extra="allow"):
    credits: int | None = None
    credit_reset_frequency: str | None = None
    extra_credit_price: float | None = None
    tracked_items: int | None = None
    csv_row_export_limit: int | None = None
    extra_csv_row_price: float | None = None
    extra_tracked_item_price: float | None = None
    max_rows_per_export: int | None = None


class AccountPlan(BaseModel, extra="allow"):
    name: str | None = None
    features: PlanFeatures | None = None


class AccountBilling(BaseModel, extra="allow"):
    billing_period: Literal["monthly", "annual"] | None = None
    next_renewal_date: str | None = None


class AccountUsage(BaseModel, extra="allow"):
    subscription_credits_remaining: int | None = None
    extra_credits_remaining: int | None = None
    extra_tracked_items: int | None = None


class AccountDetails(BaseModel, extra="allow"):
    plan: AccountPlan | None = None
    billing: AccountBilling | None = None
    usage: AccountUsage | None = None


class UsageHistoryBucket(BaseModel, extra="allow"):
    bucket: str | None = None
    subscription_used: int | None = None
    extra_used: int | None = None
    total_used: int | None = None
    extra_purchased: int | None = None


class CreditsUsageHistory(BaseModel, extra="allow"):
    range: str | None = None
    granularity: str | None = None
    generated_at: str | None = None
    credits: list[UsageHistoryBucket] | None = None
    export_rows: list[UsageHistoryBucket] | None = None
