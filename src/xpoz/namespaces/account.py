from __future__ import annotations

from typing import Any

from xpoz.namespaces._base import BaseNamespace, AsyncBaseNamespace
from xpoz._transform._field_mapping import map_dict_keys_to_snake
from xpoz.types.account import (
    AccountDetails,
    AccountPlan,
    AccountBilling,
    AccountUsage,
    PlanFeatures,
    CreditsUsageHistory,
    UsageHistoryBucket,
)
from xpoz._config import _tools


def _parse_usage_history_buckets(raw_list: Any) -> list[UsageHistoryBucket]:
    if not isinstance(raw_list, list):
        return []
    return [
        UsageHistoryBucket.model_validate(map_dict_keys_to_snake(item))
        for item in raw_list
        if isinstance(item, dict)
    ]


def _parse_credits_usage_history(raw: dict[str, Any]) -> CreditsUsageHistory:
    data_raw: Any = raw.get("data", raw)
    if not isinstance(data_raw, dict):
        return CreditsUsageHistory()
    data: dict[str, Any] = data_raw

    return CreditsUsageHistory(
        range=data.get("range"),
        granularity=data.get("granularity"),
        generated_at=data.get("generatedAt"),
        credits=_parse_usage_history_buckets(data.get("credits")),
        export_rows=_parse_usage_history_buckets(data.get("exportRows")),
    )


def _parse_account_details(raw: dict[str, Any]) -> AccountDetails:
    data_raw: Any = raw.get("data", raw)
    if not isinstance(data_raw, dict):
        return AccountDetails()
    data: dict[str, Any] = data_raw

    plan_raw = data.get("plan")
    plan: AccountPlan | None = None
    if isinstance(plan_raw, dict):
        features_raw = plan_raw.get("features")
        features: PlanFeatures | None = None
        if isinstance(features_raw, dict):
            features = PlanFeatures.model_validate(map_dict_keys_to_snake(features_raw))
        plan = AccountPlan(name=plan_raw.get("name"), features=features)

    billing_raw = data.get("billing")
    billing: AccountBilling | None = None
    if isinstance(billing_raw, dict):
        billing = AccountBilling.model_validate(map_dict_keys_to_snake(billing_raw))

    usage_raw = data.get("usage")
    usage: AccountUsage | None = None
    if isinstance(usage_raw, dict):
        usage = AccountUsage.model_validate(map_dict_keys_to_snake(usage_raw))

    return AccountDetails(plan=plan, billing=billing, usage=usage)


class AccountNamespace(BaseNamespace):
    def get_account_details(self) -> AccountDetails:
        result = self._call_and_maybe_poll(_tools.GET_ACCOUNT_DETAILS, {})
        return _parse_account_details(result)

    def get_credits_usage_history(
        self,
        *,
        range: str | None = None,
        granularity: str | None = None,
    ) -> CreditsUsageHistory:
        args = self._build_args(range=range, granularity=granularity)
        result = self._call_and_maybe_poll(_tools.GET_CREDITS_USAGE_HISTORY, args)
        return _parse_credits_usage_history(result)


class AsyncAccountNamespace(AsyncBaseNamespace):
    async def get_account_details(self) -> AccountDetails:
        result = await self._call_and_maybe_poll(_tools.GET_ACCOUNT_DETAILS, {})
        return _parse_account_details(result)

    async def get_credits_usage_history(
        self,
        *,
        range: str | None = None,
        granularity: str | None = None,
    ) -> CreditsUsageHistory:
        args = self._build_args(range=range, granularity=granularity)
        result = await self._call_and_maybe_poll(_tools.GET_CREDITS_USAGE_HISTORY, args)
        return _parse_credits_usage_history(result)
