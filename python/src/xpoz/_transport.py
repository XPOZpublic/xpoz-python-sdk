from __future__ import annotations

import json
from typing import Any

import anyio
from anyio.from_thread import BlockingPortal, start_blocking_portal
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


class McpTransport:
    def __init__(self, server_url: str, api_key: str | None = None):
        self._server_url = server_url
        self._api_key = api_key
        self._session: ClientSession | None = None
        self._context_stack: list[Any] = []

    async def connect(self) -> None:
        headers: dict[str, str] = {}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        ctx = streamablehttp_client(self._server_url, headers=headers)
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

        try:
            parsed: dict[str, Any] = json.loads(combined_text)
            return parsed
        except json.JSONDecodeError:
            return {"raw": combined_text}


class SyncTransport:
    def __init__(self, server_url: str, api_key: str | None = None):
        self._async_transport = McpTransport(server_url, api_key)
        self._portal_cm: Any = None
        self._portal: BlockingPortal | None = None

    def connect(self) -> None:
        self._portal_cm = start_blocking_portal()
        self._portal = self._portal_cm.__enter__()
        self._portal.call(self._async_transport.connect)

    def close(self) -> None:
        if self._portal:
            try:
                self._portal.call(self._async_transport.close)
            except Exception:
                pass
        if self._portal_cm:
            try:
                self._portal_cm.__exit__(None, None, None)
            except Exception:
                pass
            self._portal_cm = None
            self._portal = None

    def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if self._portal is None:
            raise RuntimeError("Transport not connected. Call connect() first.")
        result: dict[str, Any] = self._portal.call(
            self._async_transport.call_tool, tool_name, arguments
        )
        return result
