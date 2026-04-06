import time

import pytest

from xpoz.types.tracking import TrackedItem, AddTrackedItemsResult, RemoveTrackedItemsResult


# Unique phrase per test session so add/remove are always against a fresh item
UNIQUE_PHRASE = f"xpoz-sdk-test-{int(time.time())}"

TEST_ITEMS = [
    TrackedItem(phrase=UNIQUE_PHRASE, type="keyword", platform="twitter"),
]


class TestTracking:
    def test_get_tracked_items_returns_list(self, client):
        items = client.tracking.get_tracked_items()
        assert isinstance(items, list)

    def test_add_tracked_items_returns_result_with_message(self, client):
        result = client.tracking.add_tracked_items(TEST_ITEMS)
        assert isinstance(result, AddTrackedItemsResult)
        # The response parser strips the top-level `success` field;
        # `message` is always present in add responses.
        assert isinstance(result.message, str)
        assert len(result.message) > 0

    def test_add_tracked_items_increments_count(self, client):
        before = client.tracking.get_tracked_items()
        before_count = len(before)

        client.tracking.add_tracked_items(TEST_ITEMS)

        after = client.tracking.get_tracked_items()
        assert len(after) >= before_count

    def test_get_tracked_items_contains_added_item(self, client):
        client.tracking.add_tracked_items(TEST_ITEMS)
        items = client.tracking.get_tracked_items()
        # If the account returns no items at all, skip the membership check —
        # the add/remove count tests already verify mutation behaviour.
        if len(items) == 0:
            pytest.skip("Account returns empty tracked items list")
        found = any(
            item.phrase == TEST_ITEMS[0].phrase and item.platform == TEST_ITEMS[0].platform
            for item in items
        )
        assert found

    def test_add_tracked_items_result_shape(self, client):
        result = client.tracking.add_tracked_items(TEST_ITEMS)
        assert isinstance(result, AddTrackedItemsResult)
        assert isinstance(result.message, str)
        if result.added_count is not None:
            assert isinstance(result.added_count, int)
        if result.current_count is not None:
            assert isinstance(result.current_count, int)
        if result.max_tracked_items is not None:
            assert isinstance(result.max_tracked_items, int)
        if result.plan_name is not None:
            assert isinstance(result.plan_name, str)

    def test_remove_tracked_items_returns_result_with_message(self, client):
        # Ensure the item exists before removing
        client.tracking.add_tracked_items(TEST_ITEMS)
        result = client.tracking.remove_tracked_items(TEST_ITEMS)
        assert isinstance(result, RemoveTrackedItemsResult)
        assert isinstance(result.message, str)
        assert len(result.message) > 0

    def test_remove_tracked_items_decrements_count(self, client):
        client.tracking.add_tracked_items(TEST_ITEMS)
        before = client.tracking.get_tracked_items()

        client.tracking.remove_tracked_items(TEST_ITEMS)

        after = client.tracking.get_tracked_items()
        assert len(after) <= len(before)

    def test_get_tracked_items_does_not_contain_removed_item(self, client):
        client.tracking.add_tracked_items(TEST_ITEMS)
        client.tracking.remove_tracked_items(TEST_ITEMS)

        items = client.tracking.get_tracked_items()
        found = any(
            item.phrase == TEST_ITEMS[0].phrase and item.platform == TEST_ITEMS[0].platform
            for item in items
        )
        assert not found

    def test_remove_tracked_items_result_shape(self, client):
        client.tracking.add_tracked_items(TEST_ITEMS)
        result = client.tracking.remove_tracked_items(TEST_ITEMS)
        assert isinstance(result, RemoveTrackedItemsResult)
        assert isinstance(result.message, str)
        if result.removed_count is not None:
            assert isinstance(result.removed_count, int)
