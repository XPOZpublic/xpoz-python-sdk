from __future__ import annotations

import asyncio
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import pytest

from xpoz._config import _routes
from xpoz._cursor import CursorResult
from xpoz._exceptions import AuthenticationError, ValidationError
from xpoz._rest import RestTransport
from xpoz.namespaces.instagram_live import InstagramLiveNamespace

RECORDED_REQUESTS: list[tuple[str, dict[str, list[str]], dict[str, str]]] = []


def _post_page(post_id: str, cursor: str | None, has_more: bool) -> dict[str, object]:
    return {
        "results": [{"id": post_id, "username": "natgeo", "likeCount": 10}],
        "count": 1,
        "dataSource": "api",
        "has_more": has_more,
        "next_page_cursor": cursor,
    }


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *args: object) -> None:
        pass

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        RECORDED_REQUESTS.append((parsed.path, params, dict(self.headers)))

        if self.headers.get("Authorization") != "Bearer test-key":
            self._send(403, {"success": False, "message": "forbidden"})
            return

        if parsed.path == _routes.INSTAGRAM_LIVE_POSTS:
            if not params.get("q"):
                self._send(400, {"success": False, "error": "q is required"})
                return
            if params.get("cursor") == ["cur-1"]:
                self._send(200, _post_page("post-2", None, False))
                return
            self._send(200, _post_page("post-1", "cur-1", True))
            return

        if parsed.path == _routes.INSTAGRAM_LIVE_POST_INTERACTING_USERS.format(
            post_id="p1"
        ):
            self._send(
                200,
                {
                    "results": [{"id": 223214544, "username": "someone"}],
                    "count": 1,
                    "dataSource": "api",
                    "has_more": False,
                    "next_page_cursor": None,
                },
            )
            return

        if parsed.path == _routes.INSTAGRAM_LIVE_USERS:
            self._send(
                200,
                {
                    "results": [{"id": "u1", "username": "natgeo"}],
                    "count": 1,
                    "dataSource": "api",
                    "has_more": False,
                    "next_page_cursor": None,
                },
            )
            return

        if parsed.path == _routes.INSTAGRAM_LIVE_USER.format(identifier="natgeo"):
            self._send(
                200,
                {
                    "results": [{"id": "u1", "username": "natgeo"}],
                    "count": 1,
                    "dataSource": "api",
                    "has_more": False,
                    "next_page_cursor": None,
                },
            )
            return

        self._send(404, {"success": False, "message": "not found"})

    def _send(self, status: int, payload: dict[str, object]) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


@pytest.fixture(scope="module")
def base_url():
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


@pytest.fixture
def live(base_url):
    RECORDED_REQUESTS.clear()
    transport = RestTransport(base_url, "test-key")
    yield InstagramLiveNamespace(transport)
    transport.close()


def test_search_posts_returns_cursor_result(live):
    page = live.search_posts("travel", fields=["id", "like_count"])

    assert isinstance(page, CursorResult)
    assert len(page.data) == 1
    assert page.data[0].id == "post-1"
    assert page.has_more is True
    assert page.next_page_cursor == "cur-1"


def test_fields_are_sent_as_camel_case_csv(live):
    live.search_posts("travel", fields=["id", "like_count"])

    _, params, _ = RECORDED_REQUESTS[-1]
    assert params["fields"] == ["id,likeCount"]


def test_next_page_threads_the_cursor_and_terminates(live):
    first = live.search_posts("travel")
    second = first.next_page()

    _, params, _ = RECORDED_REQUESTS[-1]
    assert params["cursor"] == ["cur-1"]
    assert second.data[0].id == "post-2"
    assert second.has_more is False
    assert second.has_next_page() is False

    with pytest.raises(IndexError):
        second.next_page()


def test_iter_items_walks_every_page(live):
    page = live.search_posts("travel")
    ids = [post.id for post in page.iter_items()]

    assert ids == ["post-1", "post-2"]


def test_cursor_is_omitted_on_the_first_request(live):
    live.search_posts("travel")

    _, params, _ = RECORDED_REQUESTS[-1]
    assert "cursor" not in params


def test_single_item_routes_unwrap_the_page(live):
    user = live.get_user("natgeo")

    assert user is not None
    assert user.username == "natgeo"


def test_missing_required_query_raises_validation_error(live):
    with pytest.raises(ValidationError):
        live.search_posts("")


def test_bearer_token_is_sent(live):
    live.search_users("travel")

    _, _, headers = RECORDED_REQUESTS[-1]
    assert headers["Authorization"] == "Bearer test-key"
    assert headers["User-Agent"].startswith("xpoz-python-sdk/")


def test_rejected_auth_raises_authentication_error(base_url):
    transport = RestTransport(base_url, "wrong-key")
    try:
        with pytest.raises(AuthenticationError):
            InstagramLiveNamespace(transport).search_users("travel")
    finally:
        transport.close()


def test_integer_ids_are_coerced_to_strings(live):
    page = live.get_post_interacting_users("p1", "commenters")

    assert page.data[0].id == "223214544"


def test_async_namespace_pages_with_cursor(base_url):
    from xpoz._rest import AsyncRestTransport
    from xpoz.namespaces.instagram_live import AsyncInstagramLiveNamespace

    async def scenario():
        transport = AsyncRestTransport(base_url, "test-key")
        try:
            live = AsyncInstagramLiveNamespace(transport)
            first = await live.search_posts("travel")
            assert first.data[0].id == "post-1"
            assert first.has_next_page() is True

            second = await first.next_page()
            assert second.data[0].id == "post-2"
            assert second.has_next_page() is False
        finally:
            await transport.close()

    asyncio.run(scenario())


def test_async_iter_items_walks_every_page(base_url):
    from xpoz._rest import AsyncRestTransport
    from xpoz.namespaces.instagram_live import AsyncInstagramLiveNamespace

    async def scenario():
        transport = AsyncRestTransport(base_url, "test-key")
        try:
            live = AsyncInstagramLiveNamespace(transport)
            page = await live.search_posts("travel")
            ids = [post.id async for post in page.iter_items()]
            assert ids == ["post-1", "post-2"]
        finally:
            await transport.close()

    asyncio.run(scenario())
