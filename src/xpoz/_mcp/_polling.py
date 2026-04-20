from __future__ import annotations

import time
from typing import Any, Callable, Awaitable

import anyio

from xpoz._exceptions import (
    OperationTimeoutError,
    OperationFailedError,
    OperationCancelledError,
)

POLL_INTERVAL_SECONDS = 5
DEFAULT_TIMEOUT_SECONDS = 300

RESPONSE_STATUS_SUCCESS = "success"
RESPONSE_STATUS_ERROR = "error"
RESPONSE_STATUS_NO_DATA = "no_data"
RESPONSE_STATUS_RUNNING = "running"
RESPONSE_STATUS_CANCELLED = "cancelled"


def interpret_status(
    raw: dict[str, Any],
    operation_id: str | None = None,
) -> dict[str, Any] | None:
    status = raw.get("status")

    if status == RESPONSE_STATUS_ERROR:
        raise OperationFailedError(
            error=str(raw.get("error", "Unknown error")),
            operation_id=operation_id,
            message=raw.get("message"),
            category=raw.get("category"),
        )

    if status == RESPONSE_STATUS_CANCELLED:
        raise OperationCancelledError(operation_id)

    if (
        status == RESPONSE_STATUS_SUCCESS
        or status == RESPONSE_STATUS_NO_DATA
        or "results" in raw
        or "downloadUrl" in raw
    ):
        return raw

    return None


async def wait_for_result(
    call_tool: Callable[[str, dict[str, Any]], Awaitable[dict[str, Any]]],
    operation_id: str,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    start = anyio.current_time()
    while True:
        result: dict[str, Any] = await call_tool(
            "checkOperationStatus", {"operationId": operation_id}
        )

        terminal = interpret_status(result, operation_id)
        if terminal is not None:
            return terminal

        elapsed = anyio.current_time() - start
        if elapsed >= timeout:
            raise OperationTimeoutError(operation_id, elapsed)

        await anyio.sleep(POLL_INTERVAL_SECONDS)


def wait_for_result_sync(
    call_tool: Callable[[str, dict[str, Any]], dict[str, Any]],
    operation_id: str,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    start = time.monotonic()
    while True:
        result: dict[str, Any] = call_tool(
            "checkOperationStatus", {"operationId": operation_id}
        )

        terminal = interpret_status(result, operation_id)
        if terminal is not None:
            return terminal

        elapsed = time.monotonic() - start
        if elapsed >= timeout:
            raise OperationTimeoutError(operation_id, elapsed)

        time.sleep(POLL_INTERVAL_SECONDS)
