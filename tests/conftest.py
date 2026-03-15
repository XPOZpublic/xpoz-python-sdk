import os
from datetime import date, timedelta

import pytest

from xpoz import XpozClient


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
