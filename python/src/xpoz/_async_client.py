from __future__ import annotations

import os
from typing import Any

from xpoz._transport import McpTransport
from xpoz._polling import DEFAULT_TIMEOUT_SECONDS
from xpoz._exceptions import AuthenticationError
from xpoz.namespaces.twitter import AsyncTwitterNamespace
from xpoz.namespaces.instagram import AsyncInstagramNamespace
from xpoz.namespaces.reddit import AsyncRedditNamespace

DEFAULT_SERVER_URL = "https://mcp.xpoz.com/mcp"
ENV_API_KEY = "XPOZ_API_KEY"
ENV_SERVER_URL = "XPOZ_SERVER_URL"


class AsyncXpozClient:
    def __init__(
        self,
        api_key: str | None = None,
        *,
        server_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ):
        self._api_key = api_key or os.environ.get(ENV_API_KEY)
        if not self._api_key:
            raise AuthenticationError(
                f"API key required. Pass api_key= or set {ENV_API_KEY} environment variable."
            )

        self._server_url = server_url or os.environ.get(ENV_SERVER_URL) or DEFAULT_SERVER_URL
        self._timeout = timeout
        self._transport = McpTransport(self._server_url, self._api_key)
        self._connected = False

    async def connect(self) -> None:
        if not self._connected:
            await self._transport.connect()
            self._connected = True
            self.twitter = AsyncTwitterNamespace(self._transport.call_tool, self._timeout)
            self.instagram = AsyncInstagramNamespace(self._transport.call_tool, self._timeout)
            self.reddit = AsyncRedditNamespace(self._transport.call_tool, self._timeout)

    async def close(self) -> None:
        if self._connected:
            await self._transport.close()
            self._connected = False

    async def __aenter__(self) -> AsyncXpozClient:
        await self.connect()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
