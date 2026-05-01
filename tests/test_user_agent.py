from __future__ import annotations

import pytest

from xpoz import AsyncXpozClient, XpozClient
from xpoz._mcp._transport import (
    McpTransport,
    SyncTransport,
    _BASE_USER_AGENT,
    _build_user_agent,
)
from xpoz._version import __version__


def test_base_user_agent_matches_version() -> None:
    assert _BASE_USER_AGENT == f"xpoz-python-sdk/{__version__}"


def test_build_user_agent_default_when_none() -> None:
    assert _build_user_agent(None) == _BASE_USER_AGENT


def test_build_user_agent_default_when_empty() -> None:
    assert _build_user_agent("") == _BASE_USER_AGENT


def test_build_user_agent_appends_suffix() -> None:
    assert (
        _build_user_agent("xpoz-cli/0.1.0")
        == f"{_BASE_USER_AGENT} xpoz-cli/0.1.0"
    )


@pytest.mark.parametrize(
    "bad",
    [
        "foo\r\nX-Evil: bar",
        "foo\n",
        "foo\r",
    ],
)
def test_build_user_agent_rejects_crlf(bad: str) -> None:
    with pytest.raises(ValueError):
        _build_user_agent(bad)


@pytest.mark.parametrize(
    "bad",
    [
        "foo\x00",
        "foo\x07",
        "foo\t",
    ],
)
def test_build_user_agent_rejects_control_chars(bad: str) -> None:
    with pytest.raises(ValueError):
        _build_user_agent(bad)


def test_build_user_agent_rejects_non_ascii() -> None:
    with pytest.raises(ValueError):
        _build_user_agent("xpoz-cli/é")


def test_build_user_agent_rejects_leading_or_trailing_space() -> None:
    with pytest.raises(ValueError):
        _build_user_agent(" xpoz-cli/0.1.0")
    with pytest.raises(ValueError):
        _build_user_agent("xpoz-cli/0.1.0 ")


def test_mcp_transport_default_user_agent() -> None:
    t = McpTransport("http://example.invalid", "fake-key")
    assert t._user_agent == _BASE_USER_AGENT


def test_mcp_transport_with_suffix() -> None:
    t = McpTransport(
        "http://example.invalid",
        "fake-key",
        _user_agent_suffix="xpoz-cli/0.1.0",
    )
    assert t._user_agent == f"{_BASE_USER_AGENT} xpoz-cli/0.1.0"


def test_sync_transport_default_user_agent() -> None:
    t = SyncTransport("http://example.invalid", "fake-key")
    assert t._user_agent == _BASE_USER_AGENT


def test_sync_transport_with_suffix() -> None:
    t = SyncTransport(
        "http://example.invalid",
        "fake-key",
        _user_agent_suffix="xpoz-cli/0.1.0",
    )
    assert t._user_agent == f"{_BASE_USER_AGENT} xpoz-cli/0.1.0"


def test_mcp_transport_invalid_suffix_raises() -> None:
    with pytest.raises(ValueError):
        McpTransport(
            "http://example.invalid",
            "fake-key",
            _user_agent_suffix="bad\r\nX-Evil: 1",
        )


def test_sync_transport_invalid_suffix_raises() -> None:
    with pytest.raises(ValueError):
        SyncTransport(
            "http://example.invalid",
            "fake-key",
            _user_agent_suffix="bad\r\nX-Evil: 1",
        )


def test_xpoz_client_rejects_positional_suffix() -> None:
    with pytest.raises(TypeError):
        XpozClient("key", "http://x", 30, "suffix")  # type: ignore[misc]


def test_async_xpoz_client_rejects_positional_suffix() -> None:
    with pytest.raises(TypeError):
        AsyncXpozClient("key", "http://x", 30, "suffix")  # type: ignore[misc]
