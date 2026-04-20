from __future__ import annotations

from typing import Any, Callable

import pytest

from xpoz import NoDataResult, PaginatedResult
from xpoz._exceptions import (
    OperationCancelledError,
    OperationFailedError,
    OperationTimeoutError,
)
from xpoz._mcp._polling import interpret_status, wait_for_result_sync
from xpoz.namespaces._base import BaseNamespace
from xpoz.types.reddit import RedditPost


class _CallToolStub:
    def __init__(self, responses: list[dict[str, Any]]):
        self._responses = list(responses)
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def __call__(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        self.calls.append((name, args))
        return self._responses.pop(0)


class TestInterpretStatus:
    def test_error_raises_operation_failed_with_all_attrs(self) -> None:
        raw = {
            "status": "error",
            "error": "Operation not found",
            "message": "No operation found with ID: op_xxx",
            "category": "internal",
        }
        with pytest.raises(OperationFailedError) as exc_info:
            interpret_status(raw, operation_id="op_xxx")
        err = exc_info.value
        assert err.operation_id == "op_xxx"
        assert err.error == "Operation not found"
        assert err.message == "No operation found with ID: op_xxx"
        assert err.category == "internal"

    def test_error_without_operation_id(self) -> None:
        raw = {
            "status": "error",
            "error": "Empty query",
            "category": "validation",
        }
        with pytest.raises(OperationFailedError) as exc_info:
            interpret_status(raw)
        err = exc_info.value
        assert err.operation_id is None
        assert err.error == "Empty query"
        assert err.category == "validation"
        assert "Operation failed: Empty query" in str(err)

    def test_cancelled_raises_cancelled_error(self) -> None:
        with pytest.raises(OperationCancelledError) as exc_info:
            interpret_status({"status": "cancelled"}, operation_id="op_xxx")
        assert exc_info.value.operation_id == "op_xxx"

    def test_success_returns_raw(self) -> None:
        raw = {"status": "success", "results": [{"id": 1}]}
        assert interpret_status(raw) is raw

    def test_no_data_returns_raw(self) -> None:
        raw = {"status": "no_data", "message": "no results found"}
        assert interpret_status(raw) is raw

    def test_results_key_is_terminal_without_status(self) -> None:
        raw = {"results": []}
        assert interpret_status(raw) is raw

    def test_download_url_key_is_terminal_without_status(self) -> None:
        raw = {"downloadUrl": "https://example.com/export.csv"}
        assert interpret_status(raw) is raw

    def test_running_returns_none(self) -> None:
        raw = {"status": "running", "progress": 0.5}
        assert interpret_status(raw) is None

    def test_unknown_status_returns_none(self) -> None:
        raw = {"status": "pending"}
        assert interpret_status(raw) is None


class TestWaitForResultSync:
    def test_error_raises_immediately(self) -> None:
        stub = _CallToolStub(
            [
                {
                    "status": "error",
                    "error": "Tool execution failed",
                    "message": "crawler timeout",
                    "category": "internal",
                }
            ]
        )
        with pytest.raises(OperationFailedError) as exc_info:
            wait_for_result_sync(stub, "op_xxx", timeout=10)
        assert exc_info.value.operation_id == "op_xxx"
        assert exc_info.value.error == "Tool execution failed"
        assert exc_info.value.message == "crawler timeout"
        assert len(stub.calls) == 1

    def test_success_returns_result(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import xpoz._mcp._polling as polling_mod

        monkeypatch.setattr(polling_mod.time, "sleep", lambda _s: None)
        stub = _CallToolStub(
            [
                {"status": "running"},
                {"status": "running"},
                {"status": "success", "results": [{"id": 1}]},
            ]
        )
        result = wait_for_result_sync(stub, "op_xxx", timeout=60)
        assert result["results"] == [{"id": 1}]
        assert len(stub.calls) == 3

    def test_no_data_returns_result(self) -> None:
        stub = _CallToolStub([{"status": "no_data", "message": "no matches"}])
        result = wait_for_result_sync(stub, "op_xxx", timeout=10)
        assert result["status"] == "no_data"
        assert result["message"] == "no matches"

    def test_cancelled_raises(self) -> None:
        stub = _CallToolStub([{"status": "cancelled"}])
        with pytest.raises(OperationCancelledError) as exc_info:
            wait_for_result_sync(stub, "op_xxx", timeout=10)
        assert exc_info.value.operation_id == "op_xxx"

    def test_timeout_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import xpoz._mcp._polling as polling_mod

        monkeypatch.setattr(polling_mod.time, "sleep", lambda _s: None)
        times = iter([0.0, 0.0, 100.0])
        monkeypatch.setattr(polling_mod.time, "monotonic", lambda: next(times))
        stub = _CallToolStub(
            [{"status": "running"}, {"status": "running"}]
        )
        with pytest.raises(OperationTimeoutError):
            wait_for_result_sync(stub, "op_xxx", timeout=10)


class TestCallAndMaybePoll:
    def _make_namespace(
        self, call_tool: Callable[[str, dict[str, Any]], dict[str, Any]]
    ) -> BaseNamespace:
        return BaseNamespace(call_tool=call_tool, timeout=10)

    def test_sync_error_raises_without_operation_id(self) -> None:
        stub = _CallToolStub(
            [
                {
                    "status": "error",
                    "error": "Empty query",
                    "message": "Query cannot be empty",
                    "category": "validation",
                }
            ]
        )
        ns = self._make_namespace(stub)
        with pytest.raises(OperationFailedError) as exc_info:
            ns._call_and_maybe_poll("getRedditPostsByKeywords", {"query": ""})
        err = exc_info.value
        assert err.operation_id is None
        assert err.error == "Empty query"
        assert err.category == "validation"
        assert err.message == "Query cannot be empty"
        assert len(stub.calls) == 1

    def test_sync_success_returns_results(self) -> None:
        stub = _CallToolStub([{"status": "success", "results": [{"id": 1}]}])
        ns = self._make_namespace(stub)
        result = ns._call_and_maybe_poll("someTool", {})
        assert result["results"] == [{"id": 1}]

    def test_sync_no_data_returns_raw(self) -> None:
        stub = _CallToolStub([{"status": "no_data", "message": "empty"}])
        ns = self._make_namespace(stub)
        result = ns._call_and_maybe_poll("someTool", {})
        assert result["status"] == "no_data"
        assert result["message"] == "empty"

    def test_async_operation_polls(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import xpoz._mcp._polling as polling_mod

        monkeypatch.setattr(polling_mod.time, "sleep", lambda _s: None)
        stub = _CallToolStub(
            [
                {"operationId": "op_xxx", "status": "running"},
                {"status": "running"},
                {"status": "success", "results": [{"id": 42}]},
            ]
        )
        ns = self._make_namespace(stub)
        result = ns._call_and_maybe_poll("someTool", {})
        assert result["results"] == [{"id": 42}]
        assert len(stub.calls) == 3


class TestBuildPaginatedResult:
    def test_no_data_returns_no_data_result(self) -> None:
        stub = _CallToolStub([])
        ns = BaseNamespace(call_tool=stub, timeout=10)
        raw = {"status": "no_data", "message": "no matches for query"}
        result = ns._build_paginated_result(raw, RedditPost, "searchRedditPosts", {})
        assert isinstance(result, NoDataResult)
        assert result.status == "no_data"
        assert result.message == "no matches for query"

    def test_success_returns_paginated_result(self) -> None:
        stub = _CallToolStub([])
        ns = BaseNamespace(call_tool=stub, timeout=10)
        raw = {
            "status": "success",
            "results": [],
            "pagination": {
                "tableName": "t_xxx",
                "totalRows": 0,
                "totalPages": 1,
                "pageNumber": 1,
                "pageSize": 100,
                "resultsCount": 0,
            },
        }
        result = ns._build_paginated_result(raw, RedditPost, "searchRedditPosts", {})
        assert isinstance(result, PaginatedResult)
