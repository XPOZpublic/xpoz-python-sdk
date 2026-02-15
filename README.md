# Xpoz SDK

Official SDK for the [Xpoz](https://xpoz.com) social media intelligence platform. Query Twitter/X, Instagram, and Reddit data through simple, idiomatic interfaces.

## Languages

| Language | Package | Status |
|---|---|---|
| Python | [`xpoz`](python/) | Available |
| TypeScript | `xpoz` | Coming soon |

## What is Xpoz?

Xpoz provides unified access to social media data across Twitter/X, Instagram, and Reddit. The platform indexes billions of posts, user profiles, and engagement metrics — making it possible to search, analyze, and export social media data at scale.

The SDK wraps Xpoz's [MCP](https://modelcontextprotocol.io) server, abstracting away transport, authentication, operation polling, and pagination into a clean developer-friendly API.

## Quick Start (Python)

```bash
pip install xpoz
```

```python
from xpoz import XpozClient

with XpozClient("your-api-key") as client:
    # Get a Twitter user profile
    user = client.twitter.get_user("elonmusk")
    print(f"{user.name} — {user.followers_count:,} followers")

    # Search tweets with automatic pagination
    results = client.twitter.search_posts(
        "artificial intelligence",
        start_date="2025-01-01",
        fields=["id", "text", "like_count", "retweet_count"]
    )
    print(f"Found {results.pagination.total_rows:,} tweets")

    for tweet in results.data:
        print(f"  {tweet.text[:80]}... ({tweet.like_count} likes)")

    # Fetch all pages
    all_tweets = results.get_all_pages()

    # Export to CSV
    csv_url = results.export_csv()
```

## Features

- **30 data methods** across Twitter, Instagram, and Reddit
- **Sync and async clients** — `XpozClient` and `AsyncXpozClient`
- **Automatic operation polling** — long-running queries are abstracted away
- **Server-side pagination** — `PaginatedResult` with `next_page()`, `get_page(n)`, `get_all_pages()`
- **CSV export** — `export_csv()` on any paginated result
- **Field selection** — request only the fields you need in Pythonic snake_case
- **Pydantic v2 models** — fully typed results with autocomplete support
- **Namespaced API** — `client.twitter.*`, `client.instagram.*`, `client.reddit.*`

## Platform Coverage

### Twitter/X — 12 methods

| Method | Description |
|---|---|
| `twitter.get_user(identifier)` | Get user profile by ID or username |
| `twitter.search_users(name)` | Search users by name/username |
| `twitter.get_user_connections(username, type)` | Get followers or following |
| `twitter.get_users_by_keywords(query)` | Find users by post content |
| `twitter.get_posts_by_ids(post_ids)` | Get posts by IDs (1-100) |
| `twitter.get_posts_by_author(identifier)` | Get all posts by author |
| `twitter.search_posts(query)` | Full-text search with filters |
| `twitter.get_retweets(post_id)` | Get retweets of a post |
| `twitter.get_quotes(post_id)` | Get quote tweets |
| `twitter.get_comments(post_id)` | Get replies to a post |
| `twitter.get_post_interacting_users(post_id, type)` | Get commenters/quoters/retweeters |
| `twitter.count_posts(phrase)` | Count matching tweets |

### Instagram — 9 methods

| Method | Description |
|---|---|
| `instagram.get_user(identifier)` | Get user profile by ID or username |
| `instagram.search_users(name)` | Search users by name/username |
| `instagram.get_user_connections(username, type)` | Get followers or following |
| `instagram.get_users_by_keywords(query)` | Find users by post content |
| `instagram.get_posts_by_ids(post_ids)` | Get posts by IDs |
| `instagram.get_posts_by_user(identifier)` | Get posts by user |
| `instagram.search_posts(query)` | Search posts by keywords |
| `instagram.get_comments(post_id)` | Get post comments |
| `instagram.get_post_interacting_users(post_id, type)` | Get commenters/likers |

### Reddit — 9 methods

| Method | Description |
|---|---|
| `reddit.get_user(username)` | Get user profile |
| `reddit.search_users(name)` | Search users |
| `reddit.get_users_by_keywords(query)` | Find users by post content |
| `reddit.search_posts(query)` | Search posts by keywords |
| `reddit.get_post_with_comments(post_id)` | Get post with comments |
| `reddit.search_comments(query)` | Search comments by keywords |
| `reddit.search_subreddits(query)` | Search subreddits |
| `reddit.get_subreddit_with_posts(name)` | Get subreddit with posts |
| `reddit.get_subreddits_by_keywords(query)` | Find subreddits by post content |

## Documentation

- [Python SDK documentation](python/README.md)

## Repository Structure

```
xpoz-sdk/
├── README.md              # This file
├── LICENSE                 # MIT License
├── python/                 # Python SDK
│   ├── README.md           # Python-specific docs
│   ├── pyproject.toml      # Package config
│   └── src/xpoz/           # Source code
│       ├── __init__.py     # Public exports
│       ├── _client.py      # XpozClient (sync)
│       ├── _async_client.py # AsyncXpozClient (async)
│       ├── _transport.py   # MCP Streamable HTTP transport
│       ├── _polling.py     # Operation polling abstraction
│       ├── _pagination.py  # PaginatedResult helpers
│       ├── _field_mapping.py # snake_case ↔ camelCase
│       ├── _exceptions.py  # Error hierarchy
│       ├── types/          # Pydantic v2 models
│       │   ├── twitter.py  # Tweet, TwitterUser
│       │   ├── instagram.py # InstagramPost, InstagramUser, InstagramComment
│       │   ├── reddit.py   # RedditPost, RedditUser, RedditComment, RedditSubreddit
│       │   └── common.py   # PaginationInfo
│       └── namespaces/     # Platform-specific method groups
│           ├── twitter.py  # 12 methods (sync + async)
│           ├── instagram.py # 9 methods (sync + async)
│           └── reddit.py   # 9 methods (sync + async)
└── typescript/             # TypeScript SDK (planned)
```

## License

MIT — see [LICENSE](LICENSE).
