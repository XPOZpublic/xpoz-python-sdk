from __future__ import annotations

import json
import warnings
from urllib.request import Request, urlopen

from packaging.version import Version

from xpoz._version import __version__

PYPI_URL = "https://pypi.org/pypi/xpoz/json"
PYPI_TIMEOUT_SECONDS = 3


class XpozUpdateWarning(UserWarning):
    pass


def check_for_update() -> None:
    try:
        req = Request(PYPI_URL)
        with urlopen(req, timeout=PYPI_TIMEOUT_SECONDS) as resp:
            data = json.loads(resp.read())

        current = Version(__version__)

        stable_versions = [
            Version(v)
            for v in data["releases"]
            if not Version(v).is_prerelease and not Version(v).is_devrelease
        ]
        if not stable_versions:
            return

        latest = max(stable_versions)
        if latest > current:
            warnings.warn(
                f"You are using xpoz v{current}, but v{latest} is available. "
                "Upgrade with: pip install --upgrade xpoz",
                category=XpozUpdateWarning,
                stacklevel=1,
            )
    except Exception:
        pass
