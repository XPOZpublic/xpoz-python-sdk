import pytest

from xpoz import PaginatedResult, ResponseType
from xpoz.types.twitter import TwitterPost, TwitterUser
from xpoz.types.common import PaginationInfo


@pytest.fixture(scope="module")
def twitter_search_fast_result(client, seven_days_ago):
    return client.twitter.search_posts(
        "bitcoin",
        start_date=seven_days_ago,
        fields=["id", "text", "like_count", "retweet_count"],
        response_type=ResponseType.FAST,
        limit=10,
    )


@pytest.fixture(scope="module")
def twitter_search_paging_result(client, seven_days_ago):
    return client.twitter.search_posts(
        "bitcoin",
        start_date=seven_days_ago,
        fields=["id", "text", "like_count", "retweet_count"],
        response_type=ResponseType.PAGING,
    )


@pytest.fixture(scope="module")
def twitter_csv_result(client, seven_days_ago):
    return client.twitter.search_posts(
        "bitcoin",
        start_date=seven_days_ago,
        response_type=ResponseType.CSV,
    )


@pytest.fixture(scope="module")
def twitter_users_by_keywords_fast(client, seven_days_ago):
    return client.twitter.get_users_by_keywords(
        "artificial intelligence", start_date=seven_days_ago, response_type=ResponseType.FAST, limit=10
    )


@pytest.fixture(scope="module")
def twitter_users_by_keywords_paging(client, seven_days_ago):
    return client.twitter.get_users_by_keywords(
        "artificial intelligence", start_date=seven_days_ago, response_type=ResponseType.PAGING
    )


@pytest.fixture(scope="module")
def twitter_post_id():
    return "1874266108200673750"


class TestTwitterUsers:
    def test_get_users_by_usernames(self, client):
        users = client.twitter.get_users(["elonmusk", "sama"])
        assert isinstance(users, list)
        assert len(users) == 2
        for u in users:
            assert isinstance(u, TwitterUser)
            assert u.username is not None

    def test_get_users_by_ids(self, client):
        users = client.twitter.get_users(["44196397"], identifier_type="id")
        assert isinstance(users, list)
        assert len(users) == 1
        assert isinstance(users[0], TwitterUser)
        assert users[0].id == "44196397"

    def test_get_users_with_fields(self, client):
        users = client.twitter.get_users(
            ["elonmusk"], fields=["id", "username", "followers_count"]
        )
        assert isinstance(users, list)
        assert len(users) == 1
        assert users[0].id is not None
        assert users[0].username is not None
        assert users[0].followers_count is not None

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

    def test_get_users_by_keywords_fast(self, twitter_users_by_keywords_fast):
        result = twitter_users_by_keywords_fast
        assert isinstance(result, PaginatedResult)
        assert len(result.data) > 0
        for u in result.data:
            assert isinstance(u, TwitterUser)

    def test_get_users_by_keywords_paging(self, twitter_users_by_keywords_paging):
        result = twitter_users_by_keywords_paging
        assert isinstance(result, PaginatedResult)
        assert len(result.data) > 0
        assert result.pagination.total_rows > 0
        assert result.pagination.table_name is not None


class TestTwitterPosts:
    def test_get_posts_by_author_fast(self, client, seven_days_ago):
        result = client.twitter.get_posts_by_author(
            "elonmusk", fields=["id", "text", "like_count"], start_date=seven_days_ago, response_type=ResponseType.FAST, limit=10
        )
        assert isinstance(result, PaginatedResult)
        assert len(result.data) > 0
        for post in result.data:
            assert isinstance(post, TwitterPost)
            assert post.text is not None

    def test_get_posts_by_author_paging(self, client, seven_days_ago):
        result = client.twitter.get_posts_by_author(
            "elonmusk", fields=["id", "text", "like_count"], start_date=seven_days_ago, response_type=ResponseType.PAGING
        )
        assert isinstance(result, PaginatedResult)
        assert len(result.data) > 0
        assert result.pagination.total_rows > 0
        assert result.pagination.table_name is not None

    def test_search_posts_fast(self, twitter_search_fast_result):
        result = twitter_search_fast_result
        assert isinstance(result, PaginatedResult)
        assert len(result.data) > 0

    def test_search_posts_paging(self, twitter_search_paging_result):
        result = twitter_search_paging_result
        assert isinstance(result, PaginatedResult)
        assert len(result.data) > 0
        assert result.pagination.total_rows > 0
        assert result.pagination.table_name is not None

    def test_search_posts_pagination(self, twitter_search_paging_result):
        if not twitter_search_paging_result.has_next_page():
            pytest.skip("Only one page of results")
        page2 = twitter_search_paging_result.next_page()
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
        assert isinstance(posts[0], TwitterPost)

    def test_count_posts(self, client, seven_days_ago):
        count = client.twitter.count_posts("bitcoin", start_date=seven_days_ago)
        assert isinstance(count, int)
        assert count > 0

    def test_export_csv(self, twitter_csv_result):
        url = twitter_csv_result.export_csv()
        assert isinstance(url, str)
        assert len(url) > 0
