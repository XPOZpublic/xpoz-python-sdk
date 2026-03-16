from __future__ import annotations

import os
import threading
from typing import Any

from xpoz._mcp._transport import SyncTransport
from xpoz._mcp._polling import DEFAULT_TIMEOUT_SECONDS
from xpoz._exceptions import AuthenticationError
from xpoz._config._constants import DEFAULT_SERVER_URL, ENV_API_KEY, ENV_SERVER_URL
from xpoz._update_check import check_for_update
from xpoz.namespaces.twitter import TwitterNamespace
from xpoz.namespaces.instagram import InstagramNamespace
from xpoz.namespaces.reddit import RedditNamespace


class XpozClient:
    def __init__(
        self,
        api_key: str | None = None,
        *,
        server_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        check_update: bool = True,
    ):
        self._api_key = api_key or os.environ.get(ENV_API_KEY)
        if not self._api_key:
            raise AuthenticationError(
                f"API key required. Get your token at http://xpoz.ai/get-token?utm_source=python_sdk&utm_medium=sdk "
                f"(login → copy token), then pass it as api_key= or set the {ENV_API_KEY} environment variable."
            )

        self._server_url = server_url or os.environ.get(ENV_SERVER_URL) or DEFAULT_SERVER_URL
        self._timeout = timeout
        self._transport = SyncTransport(self._server_url, self._api_key)
        self._transport.connect()

        self.twitter = TwitterNamespace(self._transport.call_tool, self._timeout)
        self.instagram = InstagramNamespace(self._transport.call_tool, self._timeout)
        self.reddit = RedditNamespace(self._transport.call_tool, self._timeout)

        if check_update:
            threading.Thread(target=check_for_update, daemon=True, name="xpoz-update-check").start()

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> XpozClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
