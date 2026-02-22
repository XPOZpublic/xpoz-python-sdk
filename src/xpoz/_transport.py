from __future__ import annotations

from typing import Any

import anyio
import httpx
from anyio.from_thread import BlockingPortal, start_blocking_portal
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from xpoz._response_parser import parse_response_text
from xpoz._version import __version__

_USER_AGENT = f"xpoz-python-sdk/{__version__}"


def _parse_tool_result(tool_name: str, result: Any) -> dict[str, Any]:
    if result.isError:
        error_text = ""
        for block in result.content:
            if hasattr(block, "text"):
                error_text += block.text
        raise RuntimeError(f"MCP tool error ({tool_name}): {error_text}")

    combined_text = ""
    for block in result.content:
        if hasattr(block, "text"):
            combined_text += block.text

    return parse_response_text(combined_text)


class McpTransport:
    def __init__(self, server_url: str, api_key: str | None = None):
        self._server_url = server_url
        self._api_key = api_key
        self._session: ClientSession | None = None
        self._context_stack: list[Any] = []

    async def connect(self) -> None:
        headers: dict[str, str] = {"User-Agent": _USER_AGENT}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        http_client = httpx.AsyncClient(
            headers=headers,
            timeout=httpx.Timeout(30, read=None),
        )
        ctx = streamable_http_client(self._server_url, http_client=http_client)
        streams = await ctx.__aenter__()
        self._context_stack.append(ctx)

        read_stream, write_stream, _ = streams
        session_ctx = ClientSession(read_stream, write_stream)
        self._session = await session_ctx.__aenter__()
        self._context_stack.append(session_ctx)

        await self._session.initialize()

    async def close(self) -> None:
        for ctx in reversed(self._context_stack):
            try:
                await ctx.__aexit__(None, None, None)
            except Exception:
                pass
        self._context_stack.clear()
        self._session = None

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if self._session is None:
            raise RuntimeError("Transport not connected. Call connect() first.")

        result = await self._session.call_tool(tool_name, arguments)
        return _parse_tool_result(tool_name, result)


class SyncTransport:
    def __init__(self, server_url: str, api_key: str | None = None):
        self._server_url = server_url
        self._api_key = api_key
        self._session: ClientSession | None = None
        self._portal_cm: Any = None
        self._portal: BlockingPortal | None = None
        self._shutdown_event: anyio.Event | None = None
        self._connect_error: BaseException | None = None

    def connect(self) -> None:
        self._portal_cm = start_blocking_portal()
        self._portal = self._portal_cm.__enter__()

        ready_event = self._portal.call(anyio.Event)
        self._shutdown_event = self._portal.call(anyio.Event)
        self._portal.start_task_soon(self._lifecycle, ready_event, self._shutdown_event)
        self._portal.call(ready_event.wait)

        if self._connect_error is not None:
            raise self._connect_error

    async def _lifecycle(
        self,
        ready: anyio.Event,
        shutdown: anyio.Event,
    ) -> None:
        try:
            headers: dict[str, str] = {"User-Agent": _USER_AGENT}
            if self._api_key:
                headers["Authorization"] = f"Bearer {self._api_key}"

            http_client = httpx.AsyncClient(
                headers=headers,
                timeout=httpx.Timeout(30, read=None),
            )
            async with streamable_http_client(self._server_url, http_client=http_client) as streams:
                read_stream, write_stream, _ = streams
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    self._session = session
                    ready.set()
                    await shutdown.wait()
        except BaseException as exc:
            self._connect_error = exc
            ready.set()
            raise
        finally:
            self._session = None

    def close(self) -> None:
        if self._portal and self._shutdown_event:
            try:
                self._portal.call(self._shutdown_event.set)
            except Exception:
                pass
        if self._portal_cm:
            try:
                self._portal_cm.__exit__(None, None, None)
            except Exception:
                pass
            self._portal_cm = None
            self._portal = None
            self._session = None

    def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if self._portal is None or self._session is None:
            raise RuntimeError("Transport not connected. Call connect() first.")

        async def _call() -> dict[str, Any]:
            assert self._session is not None
            result = await self._session.call_tool(tool_name, arguments)
            return _parse_tool_result(tool_name, result)

        return self._portal.call(_call)
