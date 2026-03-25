import pytest

from xpoz import PaginatedResult, ResponseType
from xpoz.types.tiktok import TiktokPost, TiktokUser, TiktokComment
from xpoz.types.common import PaginationInfo
from .schema_validators import assert_has_fields, assert_field_types, assert_pagination_structure


# TEMPORARILY DISABLED
# @pytest.fixture(scope="module")
# def tiktok_posts_fast_result(client, seven_days_ago):
#     return client.tiktok.get_posts_by_user(
#         "tiktok", fields=["id", "description", "like_count"], start_date=seven_days_ago, response_type=ResponseType.FAST, limit=10
#     )


# TEMPORARILY DISABLED
# @pytest.fixture(scope="module")
# def tiktok_posts_paging_result(client, seven_days_ago):
#     return client.tiktok.get_posts_by_user(
#         "tiktok", fields=["id", "description", "like_count"], start_date=seven_days_ago, response_type=ResponseType.PAGING
#     )


@pytest.fixture(scope="module")
def tiktok_search_fast_result(client, seven_days_ago):
    return client.tiktok.search_posts(
        "dance", fields=["id", "description", "like_count"], start_date=seven_days_ago, response_type=ResponseType.FAST, limit=10
    )


@pytest.fixture(scope="module")
def tiktok_search_paging_result(client, seven_days_ago):
    return client.tiktok.search_posts(
        "dance", fields=["id", "description", "like_count"], start_date=seven_days_ago, response_type=ResponseType.PAGING
    )


# TEMPORARILY DISABLED
# @pytest.fixture(scope="module")
# def tiktok_users_by_keywords_fast(client, seven_days_ago):
#     return client.tiktok.get_users_by_keywords("dance", start_date=seven_days_ago, response_type="fast", limit=10)


# TEMPORARILY DISABLED
# @pytest.fixture(scope="module")
# def tiktok_users_by_keywords_paging(client, seven_days_ago):
#     return client.tiktok.get_users_by_keywords("dance", start_date=seven_days_ago, response_type="paging")


@pytest.fixture(scope="module")
def tiktok_post_id():
    return "7566352338953227542"


class TestTiktokUsers:
    def test_get_user(self, client):
        user = client.tiktok.get_user("tiktok")
        assert isinstance(user, TiktokUser)
        assert user.username == "tiktok"
        assert_has_fields(user, ["id", "username", "nickname"], "TiktokUser")

    def test_get_user_with_fields(self, client):
        user = client.tiktok.get_user("tiktok", fields=["id", "username", "follower_count"])
        assert isinstance(user, TiktokUser)
        assert user.id is not None
        assert user.username is not None
        assert user.follower_count is not None
        assert_has_fields(user, ["id", "username", "follower_count"], "TiktokUser")
        assert_field_types(user, {"follower_count": int}, "TiktokUser")

    def test_search_users(self, client):
        users = client.tiktok.search_users("charli")
        assert isinstance(users, list)
        assert len(users) > 0
        for u in users:
            assert isinstance(u, TiktokUser)

    # TEMPORARILY DISABLED
    # def test_get_users_by_keywords_fast(self, tiktok_users_by_keywords_fast):
    #     result = tiktok_users_by_keywords_fast
    #     assert isinstance(result, PaginatedResult)
    #     assert len(result.data) > 0
    #     for u in result.data:
    #         assert isinstance(u, TiktokUser)

    # TEMPORARILY DISABLED
    # def test_get_users_by_keywords_paging(self, tiktok_users_by_keywords_paging):
    #     result = tiktok_users_by_keywords_paging
    #     assert isinstance(result, PaginatedResult)
    #     assert len(result.data) > 0
    #     assert_pagination_structure(result)


class TestTiktokPosts:
    # TEMPORARILY DISABLED
    # def test_get_posts_by_user_fast(self, tiktok_posts_fast_result):
    #     result = tiktok_posts_fast_result
    #     assert isinstance(result, PaginatedResult)
    #     assert len(result.data) > 0
    #     for post in result.data:
    #         assert isinstance(post, TiktokPost)

    # TEMPORARILY DISABLED
    # def test_get_posts_by_user_paging(self, tiktok_posts_paging_result):
    #     result = tiktok_posts_paging_result
    #     assert isinstance(result, PaginatedResult)
    #     assert len(result.data) > 0
    #     assert_pagination_structure(result)
    #     for post in result.data[:3]:
    #         assert_has_fields(post, ["id", "description"], "TiktokPost")

    def test_search_posts_fast(self, tiktok_search_fast_result):
        result = tiktok_search_fast_result
        assert isinstance(result, PaginatedResult)
        assert len(result.data) > 0

    def test_search_posts_paging(self, tiktok_search_paging_result):
        result = tiktok_search_paging_result
        assert isinstance(result, PaginatedResult)
        assert len(result.data) > 0
        assert_pagination_structure(result)

    def test_get_posts_by_ids(self, client, tiktok_post_id):
        if tiktok_post_id is None:
            pytest.skip("No post ID available")
        posts = client.tiktok.get_posts_by_ids([tiktok_post_id])
        assert isinstance(posts, list)
        assert len(posts) == 1
        assert isinstance(posts[0], TiktokPost)

    def test_get_comments(self, client, tiktok_post_id):
        if tiktok_post_id is None:
            pytest.skip("No post ID available")
        result = client.tiktok.get_comments(tiktok_post_id)
        assert isinstance(result, PaginatedResult)
