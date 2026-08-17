from __future__ import annotations

import os
import threading
from typing import Any

from xpoz._mcp._transport import SyncTransport
from xpoz._mcp._polling import DEFAULT_TIMEOUT_SECONDS
from xpoz._exceptions import AuthenticationError
from xpoz._config._constants import DEFAULT_SERVER_URL, ENV_API_KEY, ENV_SERVER_URL
from xpoz._config._routes import DEFAULT_API_URL, ENV_API_URL
from xpoz._rest import RestTransport
from xpoz._update_check import check_for_update
from xpoz.namespaces.twitter import TwitterNamespace
from xpoz.namespaces.instagram import InstagramNamespace
from xpoz.namespaces.instagram_live import InstagramLiveNamespace
from xpoz.namespaces.reddit import RedditNamespace
from xpoz.namespaces.tiktok import TiktokNamespace
from xpoz.namespaces.tracking import TrackingNamespace
from xpoz.namespaces.account import AccountNamespace


class XpozClient:
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
        self._rest_transport: RestTransport | None = None
        self._timeout = timeout
        self._transport = SyncTransport(
            self._server_url,
            self._api_key,
            _user_agent=_user_agent,
        )
        self._transport.connect()

        self.twitter = TwitterNamespace(self._transport.call_tool, self._timeout)
        self.instagram = InstagramNamespace(self._transport.call_tool, self._timeout)
        self.reddit = RedditNamespace(self._transport.call_tool, self._timeout)
        self.tiktok = TiktokNamespace(self._transport.call_tool, self._timeout)
        self.tracking = TrackingNamespace(self._transport.call_tool, self._timeout)
        self.account = AccountNamespace(self._transport.call_tool, self._timeout)

        if check_update:
            threading.Thread(target=check_for_update, daemon=True, name="xpoz-update-check").start()

    @property
    def instagram_live(self) -> InstagramLiveNamespace:
        return InstagramLiveNamespace(self._rest())

    def _rest(self) -> RestTransport:
        if self._rest_transport is None:
            self._rest_transport = RestTransport(
                self._api_url,
                self._api_key,
                _user_agent=self._user_agent_override,
            )
        return self._rest_transport

    def close(self) -> None:
        if self._rest_transport is not None:
            self._rest_transport.close()
            self._rest_transport = None
        self._transport.close()

    def __enter__(self) -> XpozClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
