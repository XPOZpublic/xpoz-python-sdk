import pytest

from xpoz import PaginatedResult
from xpoz.types.reddit import (
    RedditPost,
    RedditUser,
    RedditComment,
    RedditSubreddit,
    RedditPostWithComments,
    SubredditWithPosts,
)
from xpoz.types.common import PaginationInfo


@pytest.fixture(scope="module")
def reddit_search_result(client):
    return client.reddit.search_posts(
        "python", fields=["id", "title", "score"]
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

    def test_search_users(self, client):
        users = client.reddit.search_users("spez")
        assert isinstance(users, list)
        assert len(users) > 0
        for u in users:
            assert isinstance(u, RedditUser)

    def test_get_users_by_keywords(self, client):
        result = client.reddit.get_users_by_keywords("programming")
        assert isinstance(result, PaginatedResult)
        assert len(result.data) > 0
        for u in result.data:
            assert isinstance(u, RedditUser)


class TestRedditPosts:
    def test_search_posts(self, reddit_search_result):
        result = reddit_search_result
        assert isinstance(result, PaginatedResult)
        assert isinstance(result.pagination, PaginationInfo)
        assert result.pagination.total_rows > 0
        assert result.pagination.page_number == 1
        assert len(result.data) > 0
        for post in result.data:
            assert isinstance(post, RedditPost)

    def test_search_posts_with_subreddit(self, client):
        result = client.reddit.search_posts(
            "help", subreddit="python", fields=["id", "title", "subreddit_name"]
        )
        assert isinstance(result, PaginatedResult)
        assert len(result.data) > 0

    def test_search_posts_pagination(self, reddit_search_result):
        if not reddit_search_result.has_next_page():
            pytest.skip("Only one page of results")
        page2 = reddit_search_result.next_page()
        assert isinstance(page2, PaginatedResult)
        assert len(page2.data) > 0

    def test_get_post_with_comments(self, client, reddit_post_id):
        result = client.reddit.get_post_with_comments(reddit_post_id)
        assert isinstance(result, RedditPostWithComments)
        assert isinstance(result.post, RedditPost)
        assert isinstance(result.comments, list)

    def test_search_comments(self, client):
        result = client.reddit.search_comments("python")
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

    def test_get_subreddits_by_keywords(self, client):
        result = client.reddit.get_subreddits_by_keywords("programming")
        assert isinstance(result, PaginatedResult)
        assert len(result.data) > 0
        for s in result.data:
            assert isinstance(s, RedditSubreddit)
