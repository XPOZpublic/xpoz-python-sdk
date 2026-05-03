from __future__ import annotations

import pytest

from xpoz import AsyncXpozClient, XpozClient
from xpoz._mcp._transport import (
    McpTransport,
    SyncTransport,
    _DEFAULT_USER_AGENT,
    _resolve_user_agent,
)
from xpoz._version import __version__


def test_default_user_agent_matches_version() -> None:
    assert _DEFAULT_USER_AGENT == f"xpoz-python-sdk/{__version__}"


def test_resolve_user_agent_default_when_none() -> None:
    assert _resolve_user_agent(None) == _DEFAULT_USER_AGENT


def test_resolve_user_agent_default_when_empty() -> None:
    assert _resolve_user_agent("") == _DEFAULT_USER_AGENT


def test_resolve_user_agent_replaces_not_appends() -> None:
    assert _resolve_user_agent("xpoz-cli/0.2.0") == "xpoz-cli/0.2.0"


@pytest.mark.parametrize(
    "bad",
    [
        "foo\r\nX-Evil: bar",
        "foo\n",
        "foo\r",
    ],
)
def test_resolve_user_agent_rejects_crlf(bad: str) -> None:
    with pytest.raises(ValueError):
        _resolve_user_agent(bad)


@pytest.mark.parametrize(
    "bad",
    [
        "foo\x00",
        "foo\x07",
        "foo\t",
    ],
)
def test_resolve_user_agent_rejects_control_chars(bad: str) -> None:
    with pytest.raises(ValueError):
        _resolve_user_agent(bad)


def test_resolve_user_agent_rejects_non_ascii() -> None:
    with pytest.raises(ValueError):
        _resolve_user_agent("xpoz-cli/é")


def test_resolve_user_agent_rejects_leading_or_trailing_space() -> None:
    with pytest.raises(ValueError):
        _resolve_user_agent(" xpoz-cli/0.2.0")
    with pytest.raises(ValueError):
        _resolve_user_agent("xpoz-cli/0.2.0 ")


def test_mcp_transport_default_user_agent() -> None:
    t = McpTransport("http://example.invalid", "fake-key")
    assert t._user_agent == _DEFAULT_USER_AGENT


def test_mcp_transport_override_replaces_default() -> None:
    t = McpTransport(
        "http://example.invalid",
        "fake-key",
        _user_agent="xpoz-cli/0.2.0",
    )
    assert t._user_agent == "xpoz-cli/0.2.0"


def test_sync_transport_default_user_agent() -> None:
    t = SyncTransport("http://example.invalid", "fake-key")
    assert t._user_agent == _DEFAULT_USER_AGENT


def test_sync_transport_override_replaces_default() -> None:
    t = SyncTransport(
        "http://example.invalid",
        "fake-key",
        _user_agent="xpoz-cli/0.2.0",
    )
    assert t._user_agent == "xpoz-cli/0.2.0"


def test_mcp_transport_empty_override_yields_default() -> None:
    t = McpTransport("http://example.invalid", "fake-key", _user_agent="")
    assert t._user_agent == _DEFAULT_USER_AGENT


def test_sync_transport_empty_override_yields_default() -> None:
    t = SyncTransport("http://example.invalid", "fake-key", _user_agent="")
    assert t._user_agent == _DEFAULT_USER_AGENT


def test_mcp_transport_invalid_user_agent_raises() -> None:
    with pytest.raises(ValueError):
        McpTransport(
            "http://example.invalid",
            "fake-key",
            _user_agent="bad\r\nX-Evil: 1",
        )


def test_sync_transport_invalid_user_agent_raises() -> None:
    with pytest.raises(ValueError):
        SyncTransport(
            "http://example.invalid",
            "fake-key",
            _user_agent="bad\r\nX-Evil: 1",
        )


def test_mcp_transport_rejects_old_suffix_kwarg() -> None:
    with pytest.raises(TypeError):
        McpTransport(
            "http://example.invalid",
            "fake-key",
            _user_agent_suffix="xpoz-cli/0.2.0",  # type: ignore[call-arg]
        )


def test_sync_transport_rejects_old_suffix_kwarg() -> None:
    with pytest.raises(TypeError):
        SyncTransport(
            "http://example.invalid",
            "fake-key",
            _user_agent_suffix="xpoz-cli/0.2.0",  # type: ignore[call-arg]
        )


def test_xpoz_client_rejects_positional_user_agent() -> None:
    with pytest.raises(TypeError):
        XpozClient("key", "http://x", 30, "ua")  # type: ignore[misc]


def test_async_xpoz_client_rejects_positional_user_agent() -> None:
    with pytest.raises(TypeError):
        AsyncXpozClient("key", "http://x", 30, "ua")  # type: ignore[misc]


def test_xpoz_client_rejects_old_suffix_kwarg() -> None:
    with pytest.raises(TypeError):
        XpozClient(api_key="key", _user_agent_suffix="xpoz-cli/0.2.0")  # type: ignore[call-arg]


def test_async_xpoz_client_rejects_old_suffix_kwarg() -> None:
    with pytest.raises(TypeError):
        AsyncXpozClient(api_key="key", _user_agent_suffix="xpoz-cli/0.2.0")  # type: ignore[call-arg]
