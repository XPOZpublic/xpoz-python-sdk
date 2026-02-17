import pytest

from xpoz import PaginatedResult
from xpoz.types.twitter import Tweet, TwitterUser
from xpoz.types.common import PaginationInfo


@pytest.fixture(scope="module")
def twitter_search_result(client):
    return client.twitter.search_posts(
        "bitcoin",
        start_date="2025-01-01",
        fields=["id", "text", "like_count", "retweet_count"],
    )


@pytest.fixture(scope="module")
def twitter_post_id():
    return "1874266108200673750"


class TestTwitterUsers:
    def test_get_user(self, client):
        user = client.twitter.get_user("elonmusk")
        assert isinstance(user, TwitterUser)
        assert user.username == "elonmusk"

    def test_get_user_by_id(self, client):
        user = client.twitter.get_user("44196397", identifier_type="id")
        assert isinstance(user, TwitterUser)
        assert user.id == "44196397"

    def test_get_user_with_fields(self, client):
        user = client.twitter.get_user(
            "elonmusk", fields=["id", "username", "followers_count"]
        )
        assert isinstance(user, TwitterUser)
        assert user.id is not None
        assert user.username is not None
        assert user.followers_count is not None

    def test_search_users(self, client):
        users = client.twitter.search_users("elon")
        assert isinstance(users, list)
        assert len(users) > 0
        for u in users:
            assert isinstance(u, TwitterUser)
            assert u.username is not None

    def test_get_user_connections(self, client):
        result = client.twitter.get_user_connections("elonmusk", "followers")
        assert isinstance(result, PaginatedResult)
        assert isinstance(result.pagination, PaginationInfo)
        assert result.pagination.total_rows > 0
        assert len(result.data) > 0
        for u in result.data:
            assert isinstance(u, TwitterUser)

    def test_get_users_by_keywords(self, client):
        result = client.twitter.get_users_by_keywords("artificial intelligence")
        assert isinstance(result, PaginatedResult)
        assert len(result.data) > 0
        for u in result.data:
            assert isinstance(u, TwitterUser)


class TestTwitterPosts:
    def test_get_posts_by_author(self, client):
        result = client.twitter.get_posts_by_author(
            "elonmusk", fields=["id", "text", "like_count"]
        )
        assert isinstance(result, PaginatedResult)
        assert len(result.data) > 0
        for post in result.data:
            assert isinstance(post, Tweet)
            assert post.text is not None

    def test_search_posts(self, twitter_search_result):
        result = twitter_search_result
        assert isinstance(result, PaginatedResult)
        assert isinstance(result.pagination, PaginationInfo)
        assert result.pagination.total_rows > 0
        assert result.pagination.page_number == 1
        assert isinstance(result.pagination.total_pages, int)

    def test_search_posts_pagination(self, twitter_search_result):
        if not twitter_search_result.has_next_page():
            pytest.skip("Only one page of results")
        page2 = twitter_search_result.next_page()
        assert isinstance(page2, PaginatedResult)
        assert len(page2.data) > 0

    def test_get_retweets(self, client, twitter_post_id):
        result = client.twitter.get_retweets(twitter_post_id)
        assert isinstance(result, PaginatedResult)

    def test_get_quotes(self, client, twitter_post_id):
        result = client.twitter.get_quotes(twitter_post_id)
        assert isinstance(result, PaginatedResult)

    def test_get_comments(self, client, twitter_post_id):
        result = client.twitter.get_comments(twitter_post_id)
        assert isinstance(result, PaginatedResult)

    def test_get_post_interacting_users(self, client, twitter_post_id):
        result = client.twitter.get_post_interacting_users(
            twitter_post_id, "commenters"
        )
        assert isinstance(result, PaginatedResult)

    def test_get_posts_by_ids(self, client, twitter_post_id):
        posts = client.twitter.get_posts_by_ids([twitter_post_id])
        assert isinstance(posts, list)
        assert len(posts) == 1
        assert isinstance(posts[0], Tweet)

    def test_count_posts(self, client):
        count = client.twitter.count_posts("bitcoin", start_date="2025-01-01")
        assert isinstance(count, int)
        assert count > 0

    def test_export_csv(self, twitter_search_result):
        try:
            url = twitter_search_result.export_csv()
            assert isinstance(url, str)
            assert len(url) > 0
        except RuntimeError:
            pytest.skip("CSV export not available for this result")
