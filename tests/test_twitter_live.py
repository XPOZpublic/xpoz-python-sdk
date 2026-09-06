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
from xpoz.namespaces.twitter_live import TwitterLiveNamespace

RECORDED_REQUESTS: list[tuple[str, dict[str, list[str]], dict[str, str]]] = []


def _tweet_page(tweet_id: str, cursor: str | None, has_more: bool) -> dict[str, object]:
    return {
        "results": [{"id": tweet_id, "authorUsername": "nasa", "likeCount": 10}],
        "count": 1,
        "dataSource": "api",
        "has_more": has_more,
        "next_page_cursor": cursor,
    }


def _user_page(user_id: object) -> dict[str, object]:
    return {
        "results": [{"id": user_id, "username": "nasa"}],
        "count": 1,
        "dataSource": "api",
        "has_more": False,
        "next_page_cursor": None,
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

        if parsed.path == _routes.TWITTER_LIVE_POSTS:
            if not params.get("q"):
                self._send(400, {"success": False, "error": "q is required"})
                return
            if params.get("cursor") == ["cur-1"]:
                self._send(200, _tweet_page("tweet-2", None, False))
                return
            self._send(200, _tweet_page("tweet-1", "cur-1", True))
            return

        if parsed.path == _routes.TWITTER_LIVE_USER_POSTS.format(username="nasa"):
            self._send(200, _tweet_page("tweet-1", None, False))
            return

        if parsed.path == _routes.TWITTER_LIVE_POST.format(post_id="123"):
            self._send(200, _tweet_page("123", None, False))
            return

        if parsed.path == _routes.TWITTER_LIVE_POST_COMMENTS.format(post_id="123"):
            self._send(200, _tweet_page("comment-1", None, False))
            return

        if parsed.path == _routes.TWITTER_LIVE_POST_QUOTES.format(post_id="123"):
            self._send(200, _tweet_page("quote-1", None, False))
            return

        if parsed.path == _routes.TWITTER_LIVE_POST_INTERACTING_USERS.format(post_id="123"):
            self._send(200, _user_page(223214544))
            return

        if parsed.path == _routes.TWITTER_LIVE_USERS:
            self._send(200, _user_page("u1"))
            return

        if parsed.path == _routes.TWITTER_LIVE_USER.format(username="nasa"):
            self._send(200, _user_page("u1"))
            return

        if parsed.path == _routes.TWITTER_LIVE_USER_CONNECTIONS.format(username="nasa"):
            self._send(200, _user_page("u2"))
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
    yield TwitterLiveNamespace(transport)
    transport.close()


def test_search_posts_returns_cursor_result(live):
    page = live.search_posts("space", fields=["id", "like_count"])

    assert isinstance(page, CursorResult)
    assert len(page.data) == 1
    assert page.data[0].id == "tweet-1"
    assert page.has_more is True
    assert page.next_page_cursor == "cur-1"


def test_search_filters_are_sent_as_camel_case_params(live):
    live.search_posts(
        "space",
        since="2026-01-01",
        until="2026-02-01",
        lang="en",
        country_code="US",
        sort_by="latest",
        fields=["id", "like_count"],
    )

    _, params, _ = RECORDED_REQUESTS[-1]
    assert params["q"] == ["space"]
    assert params["since"] == ["2026-01-01"]
    assert params["until"] == ["2026-02-01"]
    assert params["lang"] == ["en"]
    assert params["countryCode"] == ["US"]
    assert params["sortBy"] == ["latest"]
    assert params["fields"] == ["id,likeCount"]


def test_unset_filters_and_cursor_are_omitted(live):
    live.search_posts("space")

    _, params, _ = RECORDED_REQUESTS[-1]
    assert "cursor" not in params
    assert "since" not in params
    assert "sortBy" not in params


def test_next_page_threads_the_cursor_and_terminates(live):
    first = live.search_posts("space")
    second = first.next_page()

    _, params, _ = RECORDED_REQUESTS[-1]
    assert params["cursor"] == ["cur-1"]
    assert second.data[0].id == "tweet-2"
    assert second.has_next_page() is False

    with pytest.raises(IndexError):
        second.next_page()


def test_iter_items_walks_every_page(live):
    page = live.search_posts("space")
    ids = [tweet.id for tweet in page.iter_items()]

    assert ids == ["tweet-1", "tweet-2"]


def test_user_posts_route_with_date_window(live):
    live.get_posts_by_user("nasa", since="2026-01-01")

    path, params, _ = RECORDED_REQUESTS[-1]
    assert path == "/api/data/twitter/posts/users/nasa/live"
    assert params["since"] == ["2026-01-01"]


def test_single_item_routes_unwrap_the_page(live):
    tweet = live.get_post("123")
    user = live.get_user("nasa")

    assert tweet is not None
    assert tweet.id == "123"
    assert user is not None
    assert user.username == "nasa"


def test_comments_and_quotes_use_their_own_routes(live):
    comments = live.get_comments("123")
    path, _, _ = RECORDED_REQUESTS[-1]
    assert path == "/api/data/twitter/posts/123/comments/live"
    assert comments.data[0].id == "comment-1"

    quotes = live.get_quotes("123")
    path, _, _ = RECORDED_REQUESTS[-1]
    assert path == "/api/data/twitter/posts/123/quotes/live"
    assert quotes.data[0].id == "quote-1"


def test_interaction_and_connection_types_are_sent(live):
    page = live.get_post_interacting_users("123", "retweeters")
    _, params, _ = RECORDED_REQUESTS[-1]
    assert params["interactionType"] == ["retweeters"]
    assert page.data[0].id == "223214544"

    live.get_user_connections("nasa", "followers")
    path, params, _ = RECORDED_REQUESTS[-1]
    assert path == "/api/data/twitter/users/nasa/connections/live"
    assert params["connectionType"] == ["followers"]


def test_missing_required_query_raises_validation_error(live):
    with pytest.raises(ValidationError):
        live.search_posts("")


def test_bearer_token_is_sent(live):
    live.search_users("nasa")

    _, _, headers = RECORDED_REQUESTS[-1]
    assert headers["Authorization"] == "Bearer test-key"
    assert headers["User-Agent"].startswith("xpoz-python-sdk/")


def test_rejected_auth_raises_authentication_error(base_url):
    transport = RestTransport(base_url, "wrong-key")
    try:
        with pytest.raises(AuthenticationError):
            TwitterLiveNamespace(transport).search_users("nasa")
    finally:
        transport.close()


def test_async_namespace_pages_with_cursor(base_url):
    from xpoz._rest import AsyncRestTransport
    from xpoz.namespaces.twitter_live import AsyncTwitterLiveNamespace

    async def scenario():
        transport = AsyncRestTransport(base_url, "test-key")
        try:
            live = AsyncTwitterLiveNamespace(transport)
            first = await live.search_posts("space")
            assert first.data[0].id == "tweet-1"
            assert first.has_next_page() is True

            second = await first.next_page()
            assert second.data[0].id == "tweet-2"
            assert second.has_next_page() is False

            user = await live.get_user("nasa")
            assert user is not None and user.username == "nasa"
        finally:
            await transport.close()

    asyncio.run(scenario())


def test_async_iter_items_walks_every_page(base_url):
    from xpoz._rest import AsyncRestTransport
    from xpoz.namespaces.twitter_live import AsyncTwitterLiveNamespace

    async def scenario():
        transport = AsyncRestTransport(base_url, "test-key")
        try:
            live = AsyncTwitterLiveNamespace(transport)
            page = await live.search_posts("space")
            ids = [tweet.id async for tweet in page.iter_items()]
            assert ids == ["tweet-1", "tweet-2"]
        finally:
            await transport.close()

    asyncio.run(scenario())
