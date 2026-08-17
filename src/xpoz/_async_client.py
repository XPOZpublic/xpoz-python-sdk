from __future__ import annotations

import os
import threading
from typing import Any

from xpoz._mcp._transport import McpTransport
from xpoz._mcp._polling import DEFAULT_TIMEOUT_SECONDS
from xpoz._exceptions import AuthenticationError
from xpoz._config._constants import DEFAULT_SERVER_URL, ENV_API_KEY, ENV_SERVER_URL
from xpoz._config._routes import DEFAULT_API_URL, ENV_API_URL
from xpoz._rest import AsyncRestTransport
from xpoz._update_check import check_for_update
from xpoz.namespaces.twitter import AsyncTwitterNamespace
from xpoz.namespaces.instagram import AsyncInstagramNamespace
from xpoz.namespaces.instagram_live import AsyncInstagramLiveNamespace
from xpoz.namespaces.reddit import AsyncRedditNamespace
from xpoz.namespaces.tiktok import AsyncTiktokNamespace
from xpoz.namespaces.tracking import AsyncTrackingNamespace
from xpoz.namespaces.account import AsyncAccountNamespace


class AsyncXpozClient:
    def __init__(
        self,
        api_key: str | None = None,
        *,
        server_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        check_update: bool = True,
        api_url: str | None = None,
        _user_agent: str | None = None,
    ):
        """
        _user_agent: Private API. Reserved for first-party Xpoz clients
        (CLI, IDE plugins, etc.) to set their own canonical User-Agent for
        server-side telemetry. When set, replaces the SDK's default
        User-Agent entirely. Not part of the public API; may change or be
        removed without notice. Public users should not pass this parameter.
        """
        self._api_key = api_key or os.environ.get(ENV_API_KEY)
        if not self._api_key:
            raise AuthenticationError(
                f"API key required. Get your token at http://xpoz.ai/get-token?utm_source=python_sdk&utm_medium=sdk "
                f"(login → copy token), then pass it as api_key= or set the {ENV_API_KEY} environment variable."
            )

        self._server_url = server_url or os.environ.get(ENV_SERVER_URL) or DEFAULT_SERVER_URL
        self._api_url = api_url or os.environ.get(ENV_API_URL) or DEFAULT_API_URL
        self._user_agent_override = _user_agent
        self._rest_transport: AsyncRestTransport | None = None
        self._timeout = timeout
        self._transport = McpTransport(
            self._server_url,
            self._api_key,
            _user_agent=_user_agent,
        )
        self._connected = False
        self._check_update = check_update

    def __getattr__(self, name: str) -> object:
        if name in ("twitter", "instagram", "reddit", "tiktok", "tracking", "account"):
            raise RuntimeError(
                f"AsyncXpozClient.{name} is not available. "
                "Call 'await client.connect()' or use 'async with client' first."
            )
        raise AttributeError(name)

    async def connect(self) -> None:
        if not self._connected:
            await self._transport.connect()
            self._connected = True
            self.twitter = AsyncTwitterNamespace(self._transport.call_tool, self._timeout)
            self.instagram = AsyncInstagramNamespace(self._transport.call_tool, self._timeout)
            self.reddit = AsyncRedditNamespace(self._transport.call_tool, self._timeout)
            self.tiktok = AsyncTiktokNamespace(self._transport.call_tool, self._timeout)
            self.tracking = AsyncTrackingNamespace(self._transport.call_tool, self._timeout)
            self.account = AsyncAccountNamespace(self._transport.call_tool, self._timeout)

            if self._check_update:
                threading.Thread(target=check_for_update, daemon=True, name="xpoz-update-check").start()

    @property
    def instagram_live(self) -> AsyncInstagramLiveNamespace:
        return AsyncInstagramLiveNamespace(self._rest())

    def _rest(self) -> AsyncRestTransport:
        if self._rest_transport is None:
            self._rest_transport = AsyncRestTransport(
                self._api_url,
                self._api_key,
                _user_agent=self._user_agent_override,
            )
        return self._rest_transport

    async def close(self) -> None:
        if self._rest_transport is not None:
            await self._rest_transport.close()
            self._rest_transport = None
        if self._connected:
            await self._transport.close()
            self._connected = False

    async def __aenter__(self) -> AsyncXpozClient:
        await self.connect()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
