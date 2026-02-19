import os

import pytest

from xpoz import XpozClient


@pytest.fixture(scope="module")
def client():
    api_key = os.environ.get("XPOZ_API_KEY")
    server_url = os.environ.get("XPOZ_SERVER_URL")
    if not api_key:
        pytest.skip("XPOZ_API_KEY not set")
    c = XpozClient(api_key=api_key, server_url=server_url, timeout=600)
    yield c
    c.close()
