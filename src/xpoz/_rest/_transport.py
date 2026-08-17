from __future__ import annotations

from typing import Any

import httpx

from xpoz._exceptions import (
    AuthenticationError,
    NotFoundError,
    ValidationError,
    XpozConnectionError,
    XpozError,
)
from xpoz._mcp._transport import _resolve_user_agent

_HTTP_TIMEOUT_SECONDS = 120.0


def _build_headers(api_key: str | None, user_agent: str | None) -> dict[str, str]:
    headers = {"User-Agent": _resolve_user_agent(user_agent)}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def _raise_for_status(response: httpx.Response) -> None:
    if response.status_code < 400:
        return

    try:
        payload = response.json()
        message = payload.get("error") or payload.get("message") or response.text
    except ValueError:
        message = response.text

    if response.status_code in (401, 403):
        raise AuthenticationError(message)
    if response.status_code == 404:
        raise NotFoundError(message)
    if response.status_code == 400:
        raise ValidationError(message)
    raise XpozError(f"HTTP {response.status_code}: {message}")


def _clean_params(params: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in params.items() if value is not None}


class RestTransport:
    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        *,
        timeout: float = _HTTP_TIMEOUT_SECONDS,
        _user_agent: str | None = None,
    ):
        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            headers=_build_headers(api_key, _user_agent),
            timeout=timeout,
        )

    def get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        try:
            response = self._client.get(path, params=_clean_params(params))
        except httpx.HTTPError as error:
            raise XpozConnectionError(str(error)) from error

        _raise_for_status(response)
        payload: dict[str, Any] = response.json()
        return payload

    def close(self) -> None:
        self._client.close()


class AsyncRestTransport:
    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        *,
        timeout: float = _HTTP_TIMEOUT_SECONDS,
        _user_agent: str | None = None,
    ):
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            headers=_build_headers(api_key, _user_agent),
            timeout=timeout,
        )

    async def get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        try:
            response = await self._client.get(path, params=_clean_params(params))
        except httpx.HTTPError as error:
            raise XpozConnectionError(str(error)) from error

        _raise_for_status(response)
        payload: dict[str, Any] = response.json()
        return payload

    async def close(self) -> None:
        await self._client.aclose()
