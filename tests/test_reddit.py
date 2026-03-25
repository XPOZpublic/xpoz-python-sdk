import pytest

from xpoz import PaginatedResult, ResponseType
from xpoz.types.reddit import (
    RedditPost,
    RedditUser,
    RedditComment,
    RedditSubreddit,
    RedditPostWithComments,
    SubredditWithPosts,
)
from xpoz.types.common import PaginationInfo
from .schema_validators import assert_has_fields, assert_pagination_structure


@pytest.fixture(scope="module")
def reddit_search_fast_result(client, seven_days_ago):
    return client.reddit.search_posts(
        "python", fields=["id", "title", "score"], start_date=seven_days_ago, response_type=ResponseType.FAST, limit=10
    )


@pytest.fixture(scope="module")
def reddit_search_paging_result(client, seven_days_ago):
    return client.reddit.search_posts(
        "python", fields=["id", "title", "score"], start_date=seven_days_ago, response_type=ResponseType.PAGING
    )


@pytest.fixture(scope="module")
def reddit_post_id():
    return "1l4da15"


class TestRedditUsers:
    def test_get_user(self, client):
        user = client.reddit.get_user("spez")
        assert isinstance(user, RedditUser)
        if getattr(user, "error", None):
            pytest.skip(f"Server error: {user.error}")
        assert user.username == "spez"
        assert_has_fields(user, ["id", "username", "total_karma"], "RedditUser")

    def test_search_users(self, client):
        users = client.reddit.search_users("spez")
        assert isinstance(users, list)
        assert len(users) > 0
        for u in users:
            assert isinstance(u, RedditUser)

    def test_get_users_by_keywords(self, client, seven_days_ago):
        result = client.reddit.get_users_by_keywords("programming", start_date=seven_days_ago)
        assert isinstance(result, PaginatedResult)
        assert len(result.data) > 0
        for u in result.data:
            assert isinstance(u, RedditUser)


class TestRedditPosts:
    def test_search_posts_fast(self, reddit_search_fast_result):
        result = reddit_search_fast_result
        assert isinstance(result, PaginatedResult)
        assert len(result.data) > 0
        for post in result.data:
            assert isinstance(post, RedditPost)

    def test_search_posts_paging(self, reddit_search_paging_result):
        result = reddit_search_paging_result
        assert isinstance(result, PaginatedResult)
        assert len(result.data) > 0
        assert_pagination_structure(result)

    def test_search_posts_with_subreddit(self, client, seven_days_ago):
        result = client.reddit.search_posts(
            "help", subreddit="python", fields=["id", "title", "subreddit_name"], start_date=seven_days_ago
        )
        assert isinstance(result, PaginatedResult)
        assert len(result.data) > 0

    def test_search_posts_pagination(self, reddit_search_paging_result):
        if not reddit_search_paging_result.has_next_page():
            pytest.skip("Only one page of results")
        page2 = reddit_search_paging_result.next_page()
        assert isinstance(page2, PaginatedResult)
        assert len(page2.data) > 0

    def test_get_post_with_comments(self, client, reddit_post_id):
        result = client.reddit.get_post_with_comments(reddit_post_id)
        assert isinstance(result, RedditPostWithComments)
        assert isinstance(result.post, RedditPost)
        assert isinstance(result.comments, list)

    def test_search_comments(self, client, seven_days_ago):
        result = client.reddit.search_comments("python", start_date=seven_days_ago)
        assert isinstance(result, PaginatedResult)
        assert len(result.data) > 0
        for c in result.data:
            assert isinstance(c, RedditComment)


class TestRedditSubreddits:
    def test_search_subreddits(self, client):
        subreddits = client.reddit.search_subreddits("python")
        assert isinstance(subreddits, list)
        if len(subreddits) == 0:
            pytest.skip("Server returned empty results (transient)")
        for s in subreddits:
            assert isinstance(s, RedditSubreddit)

    def test_get_subreddit_with_posts(self, client):
        result = client.reddit.get_subreddit_with_posts("python")
        assert isinstance(result, SubredditWithPosts)
        assert isinstance(result.subreddit, RedditSubreddit)
        assert result.subreddit.display_name is not None
        assert isinstance(result.posts, list)

    def test_get_subreddits_by_keywords(self, client, seven_days_ago):
        result = client.reddit.get_subreddits_by_keywords("programming", start_date=seven_days_ago)
        assert isinstance(result, PaginatedResult)
        assert len(result.data) > 0
        for s in result.data:
            assert isinstance(s, RedditSubreddit)
