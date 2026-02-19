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
        status = result.get("status")

        if status == "completed" or "results" in result or "downloadUrl" in result:
            return result

        if status == "failed":
            error = result.get("error", "Unknown error")
            raise OperationFailedError(operation_id, str(error))

        if status == "cancelled":
            raise OperationCancelledError(operation_id)

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
        status = result.get("status")

        if status == "completed" or "results" in result or "downloadUrl" in result:
            return result

        if status == "failed":
            error = result.get("error", "Unknown error")
            raise OperationFailedError(operation_id, str(error))

        if status == "cancelled":
            raise OperationCancelledError(operation_id)

        elapsed = time.monotonic() - start
        if elapsed >= timeout:
            raise OperationTimeoutError(operation_id, elapsed)

        time.sleep(POLL_INTERVAL_SECONDS)
