import pytest

from xpoz import PaginatedResult
from xpoz.types.instagram import InstagramPost, InstagramUser, InstagramComment
from xpoz.types.common import PaginationInfo


@pytest.fixture(scope="module")
def instagram_posts_result(client):
    return client.instagram.get_posts_by_user(
        "instagram", fields=["id", "caption", "like_count"]
    )


@pytest.fixture(scope="module")
def instagram_post_id(instagram_posts_result):
    assert len(instagram_posts_result.data) > 0
    return instagram_posts_result.data[0].id


class TestInstagramUsers:
    def test_get_user(self, client):
        user = client.instagram.get_user("instagram")
        assert isinstance(user, InstagramUser)
        assert user.username == "instagram"

    def test_get_user_with_fields(self, client):
        user = client.instagram.get_user(
            "instagram", fields=["id", "username", "follower_count"]
        )
        assert isinstance(user, InstagramUser)
        assert user.id is not None
        assert user.username is not None
        assert user.follower_count is not None

    @pytest.mark.skip(reason="Server operation takes >5 minutes")
    def test_search_users(self, client):
        users = client.instagram.search_users("nike")
        assert isinstance(users, list)
        assert len(users) > 0
        for u in users:
            assert isinstance(u, InstagramUser)

    @pytest.mark.skip(reason="Server operation takes >5 minutes")
    def test_get_user_connections(self, client):
        result = client.instagram.get_user_connections("instagram", "followers")
        assert isinstance(result, PaginatedResult)
        assert isinstance(result.pagination, PaginationInfo)
        assert len(result.data) > 0
        for u in result.data:
            assert isinstance(u, InstagramUser)

    @pytest.mark.skip(reason="Server operation takes >5 minutes")
    def test_get_users_by_keywords(self, client):
        result = client.instagram.get_users_by_keywords("fashion")
        assert isinstance(result, PaginatedResult)
        assert len(result.data) > 0
        for u in result.data:
            assert isinstance(u, InstagramUser)


class TestInstagramPosts:
    def test_get_posts_by_user(self, instagram_posts_result):
        result = instagram_posts_result
        assert isinstance(result, PaginatedResult)
        assert len(result.data) > 0
        for post in result.data:
            assert isinstance(post, InstagramPost)

    @pytest.mark.skip(reason="Server operation takes >5 minutes")
    def test_search_posts(self, client):
        result = client.instagram.search_posts(
            "travel", fields=["id", "caption", "like_count"]
        )
        assert isinstance(result, PaginatedResult)
        assert isinstance(result.pagination, PaginationInfo)
        assert result.pagination.total_rows > 0

    def test_get_posts_by_ids(self, client, instagram_post_id):
        posts = client.instagram.get_posts_by_ids([instagram_post_id])
        assert isinstance(posts, list)
        assert len(posts) == 1
        assert isinstance(posts[0], InstagramPost)

    @pytest.mark.skip(reason="Server operation takes >5 minutes")
    def test_get_comments(self, client, instagram_post_id):
        result = client.instagram.get_comments(instagram_post_id)
        assert isinstance(result, PaginatedResult)

    @pytest.mark.skip(reason="Server operation takes >5 minutes")
    def test_get_post_interacting_users(self, client, instagram_post_id):
        result = client.instagram.get_post_interacting_users(
            instagram_post_id, "commenters"
        )
        assert isinstance(result, PaginatedResult)
