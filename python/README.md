# Xpoz Python SDK

Python SDK for the [Xpoz](https://xpoz.com) social media intelligence platform. Query Twitter/X, Instagram, and Reddit data through a simple, Pythonic interface.

## Installation

```bash
pip install xpoz
```

## Quick Start

```python
from xpoz import XpozClient

client = XpozClient("your-api-key")

# Get a Twitter user
user = client.twitter.get_user("elonmusk")
print(user.username, user.followers_count)

# Search tweets
results = client.twitter.search_posts("artificial intelligence", start_date="2025-01-01")
for tweet in results.data:
    print(tweet.text, tweet.like_count)

# Pagination is automatic
if results.has_next_page():
    page2 = results.next_page()

# Get all pages at once
all_tweets = results.get_all_pages()

# Export to CSV
csv_url = results.export_csv()

client.close()
```

## Authentication

```python
# Pass API key directly
client = XpozClient("your-api-key")

# Or set XPOZ_API_KEY environment variable
client = XpozClient()

# Custom server URL
client = XpozClient("your-api-key", server_url="https://custom.server/mcp")
```

## Async Usage

```python
import asyncio
from xpoz import AsyncXpozClient

async def main():
    async with AsyncXpozClient("your-api-key") as client:
        user = await client.twitter.get_user("elonmusk")
        results = await client.twitter.search_posts("AI")
        page2 = await results.next_page()

asyncio.run(main())
```

## API Reference

### Twitter — `client.twitter`

| Method | Description | Returns |
|---|---|---|
| `get_posts_by_ids(post_ids)` | Get posts by IDs (1-100) | `list[Tweet]` |
| `get_posts_by_author(identifier)` | Get all posts by author | `PaginatedResult[Tweet]` |
| `search_posts(query)` | Search posts by keywords | `PaginatedResult[Tweet]` |
| `get_retweets(post_id)` | Get retweets of a post | `PaginatedResult[Tweet]` |
| `get_quotes(post_id)` | Get quote posts | `PaginatedResult[Tweet]` |
| `get_comments(post_id)` | Get replies to a post | `PaginatedResult[Tweet]` |
| `get_post_interacting_users(post_id, interaction_type)` | Get users who interacted | `PaginatedResult[TwitterUser]` |
| `count_posts(phrase)` | Count matching tweets | `int` |
| `get_user(identifier)` | Get user profile | `TwitterUser` |
| `search_users(name)` | Search users by name | `list[TwitterUser]` |
| `get_user_connections(username, connection_type)` | Get followers/following | `PaginatedResult[TwitterUser]` |
| `get_users_by_keywords(query)` | Find users by post content | `PaginatedResult[TwitterUser]` |

### Instagram — `client.instagram`

| Method | Description | Returns |
|---|---|---|
| `get_posts_by_ids(post_ids)` | Get posts by IDs | `list[InstagramPost]` |
| `get_posts_by_user(identifier)` | Get posts by user | `PaginatedResult[InstagramPost]` |
| `search_posts(query)` | Search posts by keywords | `PaginatedResult[InstagramPost]` |
| `get_comments(post_id)` | Get post comments | `PaginatedResult[InstagramComment]` |
| `get_user(identifier)` | Get user profile | `InstagramUser` |
| `search_users(name)` | Search users by name | `list[InstagramUser]` |
| `get_user_connections(username, connection_type)` | Get followers/following | `PaginatedResult[InstagramUser]` |
| `get_post_interacting_users(post_id, interaction_type)` | Get interacting users | `PaginatedResult[InstagramUser]` |
| `get_users_by_keywords(query)` | Find users by post content | `PaginatedResult[InstagramUser]` |

### Reddit — `client.reddit`

| Method | Description | Returns |
|---|---|---|
| `search_posts(query)` | Search posts by keywords | `PaginatedResult[RedditPost]` |
| `get_post_with_comments(post_id)` | Get post with comments | `RedditPostWithComments` |
| `search_comments(query)` | Search comments | `PaginatedResult[RedditComment]` |
| `get_user(username)` | Get user profile | `RedditUser` |
| `search_users(name)` | Search users | `list[RedditUser]` |
| `get_users_by_keywords(query)` | Find users by post content | `PaginatedResult[RedditUser]` |
| `search_subreddits(query)` | Search subreddits | `list[RedditSubreddit]` |
| `get_subreddit_with_posts(subreddit_name)` | Get subreddit with posts | `SubredditWithPosts` |
| `get_subreddits_by_keywords(query)` | Find subreddits by post content | `PaginatedResult[RedditSubreddit]` |

### Field Selection

All methods accept a `fields` parameter for selective field retrieval. Use snake_case — the SDK handles conversion automatically.

```python
results = client.twitter.search_posts(
    "AI",
    fields=["id", "text", "like_count", "retweet_count", "created_at_date"]
)
```

### PaginatedResult

```python
result.data                    # list[T] — current page items
result.pagination.total_rows   # total matching rows
result.pagination.total_pages  # total pages
result.has_next_page()         # bool

page2 = result.next_page()     # fetch next page
page5 = result.get_page(5)     # jump to page 5
all_data = result.get_all_pages()  # fetch all pages, returns flat list
csv_url = result.export_csv()  # export to CSV, returns download URL
```

## License

MIT
