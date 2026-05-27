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
)
from xpoz._config import _tools


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


class AsyncAccountNamespace(AsyncBaseNamespace):
    async def get_account_details(self) -> AccountDetails:
        result = await self._call_and_maybe_poll(_tools.GET_ACCOUNT_DETAILS, {})
        return _parse_account_details(result)
