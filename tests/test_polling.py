from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable

import pytest

from xpoz._exceptions import OperationCancelledError, OperationFailedError
from xpoz._mcp._polling import wait_for_result, wait_for_result_sync
from xpoz.namespaces._base import AsyncBaseNamespace, BaseNamespace


def _sync_mock(
    responses: list[dict[str, Any]],
) -> Callable[[str, dict[str, Any]], dict[str, Any]]:
    it = iter(responses)

    def mock(_name: str, _args: dict[str, Any]) -> dict[str, Any]:
        return next(it)

    return mock


def _async_mock(
    responses: list[dict[str, Any]],
) -> Callable[[str, dict[str, Any]], Awaitable[dict[str, Any]]]:
    it = iter(responses)

    async def mock(_name: str, _args: dict[str, Any]) -> dict[str, Any]:
        return next(it)

    return mock


def test_polling_sync_raises_on_status_error() -> None:
    mock = _sync_mock(
        [{"status": "error", "error": "Operation not found", "category": "internal"}]
    )
    with pytest.raises(OperationFailedError) as exc:
        wait_for_result_sync(mock, "op_abc", timeout=10)
    assert exc.value.error == "Operation not found"
    assert exc.value.operation_id == "op_abc"


def test_polling_sync_returns_on_status_success() -> None:
    response = {"status": "success", "results": [{"id": "1"}], "pagination": {}}
    mock = _sync_mock([response])
    assert wait_for_result_sync(mock, "op_abc", timeout=10) == response


def test_polling_sync_raises_on_status_cancelled() -> None:
    mock = _sync_mock([{"status": "cancelled"}])
    with pytest.raises(OperationCancelledError) as exc:
        wait_for_result_sync(mock, "op_abc", timeout=10)
    assert exc.value.operation_id == "op_abc"


def test_call_and_maybe_poll_raises_on_sync_error() -> None:
    mock = _sync_mock(
        [{"status": "error", "error": "Empty query", "category": "validation"}]
    )
    ns = BaseNamespace(mock, timeout=10)
    with pytest.raises(OperationFailedError) as exc:
        ns._call_and_maybe_poll("getRedditPostsByKeywords", {})
    assert exc.value.operation_id == ""
    assert exc.value.error == "Empty query"


def test_call_and_maybe_poll_polls_when_operation_id_present() -> None:
    mock = _sync_mock(
        [
            {"operationId": "op_x"},
            {"status": "success", "results": [{"id": "1"}]},
        ]
    )
    ns = BaseNamespace(mock, timeout=10)
    result = ns._call_and_maybe_poll("getTwitterPostsByKeywords", {})
    assert result["results"] == [{"id": "1"}]


def test_call_and_maybe_poll_returns_sync_success_with_results() -> None:
    mock = _sync_mock([{"results": [{"id": "1"}]}])
    ns = BaseNamespace(mock, timeout=10)
    result = ns._call_and_maybe_poll("searchTwitterUsers", {})
    assert result["results"] == [{"id": "1"}]


def test_async_polling_raises_on_status_error() -> None:
    mock = _async_mock([{"status": "error", "error": "Crawler failed"}])

    async def run() -> None:
        with pytest.raises(OperationFailedError) as exc:
            await wait_for_result(mock, "op_abc", timeout=10)
        assert exc.value.error == "Crawler failed"
        assert exc.value.operation_id == "op_abc"

    asyncio.run(run())


def test_async_call_and_maybe_poll_raises_on_sync_error() -> None:
    mock = _async_mock(
        [{"status": "error", "error": "Auth failed", "category": "authentication"}]
    )
    ns = AsyncBaseNamespace(mock, timeout=10)

    async def run() -> None:
        with pytest.raises(OperationFailedError) as exc:
            await ns._call_and_maybe_poll("getUserAccessKey", {})
        assert exc.value.operation_id == ""
        assert exc.value.error == "Auth failed"

    asyncio.run(run())
