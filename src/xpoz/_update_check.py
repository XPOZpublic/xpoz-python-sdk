from __future__ import annotations

import json
import warnings
from urllib.request import Request, urlopen

from xpoz._version import __version__

PYPI_URL = "https://pypi.org/pypi/xpoz/json"
PYPI_TIMEOUT_SECONDS = 3


class XpozUpdateWarning(UserWarning):
    pass


def _parse_version(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in v.split("."))


def check_for_update() -> None:
    try:
        req = Request(PYPI_URL)
        with urlopen(req, timeout=PYPI_TIMEOUT_SECONDS) as resp:
            data = json.loads(resp.read())

        latest_str = data["info"]["version"]
        if _parse_version(latest_str) > _parse_version(__version__):
            warnings.warn(
                f"You are using xpoz v{__version__}, but v{latest_str} is available. "
                "Upgrade with: pip install --upgrade xpoz",
                category=XpozUpdateWarning,
                stacklevel=1,
            )
    except Exception:
        pass
