import os
import time
from datetime import date, timedelta

import anyio
import httpx
import pytest

from xpoz import XpozClient

MIN_REQUEST_INTERVAL_SECONDS = float(os.environ.get("XPOZ_TEST_MIN_REQUEST_INTERVAL", "3.5"))

_last_request_at = 0.0


async def _pace_request(request: httpx.Request) -> None:
    global _last_request_at
    wait = MIN_REQUEST_INTERVAL_SECONDS - (time.monotonic() - _last_request_at)
    if wait > 0:
        await anyio.sleep(wait)
    _last_request_at = time.monotonic()


def _install_request_pacing() -> None:
    original_init = httpx.AsyncClient.__init__

    def paced_init(self, *args, **kwargs):
        hooks = dict(kwargs.get("event_hooks") or {})
        hooks["request"] = [*hooks.get("request", []), _pace_request]
        kwargs["event_hooks"] = hooks
        original_init(self, *args, **kwargs)

    httpx.AsyncClient.__init__ = paced_init


if MIN_REQUEST_INTERVAL_SECONDS > 0:
    _install_request_pacing()


@pytest.fixture(scope="session")
def seven_days_ago():
    return (date.today() - timedelta(days=7)).isoformat()


@pytest.fixture(scope="module")
def client():
    api_key = os.environ.get("XPOZ_API_KEY")
    server_url = os.environ.get("XPOZ_SERVER_URL")
    if not api_key:
        pytest.skip("XPOZ_API_KEY not set")
    c = XpozClient(api_key=api_key, server_url=server_url, timeout=600)
    yield c
    c.close()
