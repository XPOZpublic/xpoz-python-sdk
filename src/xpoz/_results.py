from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class NoDataResult:
    message: str
    status: Literal["no_data"] = "no_data"
