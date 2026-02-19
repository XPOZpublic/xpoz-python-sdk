# Xpoz Python SDK

Python SDK for the [Xpoz](https://xpoz.ai) social media intelligence platform. Query Twitter/X, Instagram, and Reddit data through a simple, Pythonic interface.

## Installation

```bash
pip install xpoz
```

Requires Python 3.10+.

## What is Xpoz?

Xpoz provides unified access to social media data across Twitter/X, Instagram, and Reddit. The platform indexes billions of posts, user profiles, and engagement metrics — making it possible to search, analyze, and export social media data at scale.

The SDK wraps Xpoz's [MCP](https://modelcontextprotocol.io) server, abstracting away transport, authentication, operation polling, and pagination into a clean developer-friendly API.

## Features

- **30 data methods** across Twitter, Instagram, and Reddit
- **Sync and async clients** — `XpozClient` and `AsyncXpozClient`
- **Automatic operation polling** — long-running queries are abstracted away
- **Server-side pagination** — `PaginatedResult` with `next_page()`, `get_page(n)`, `get_all_pages()`
- **CSV export** — `export_csv()` on any paginated result
- **Field selection** — request only the fields you need in Pythonic snake_case
- **Pydantic v2 models** — fully typed results with autocomplete support
- **Namespaced API** — `client.twitter.*`, `client.instagram.*`, `client.reddit.*`

## Quick Start

```python
from xpoz import XpozClient

client = XpozClient("your-api-key")

user = client.twitter.get_user("elonmusk")
print(f"{user.name} — {user.followers_count:,} followers")

results = client.twitter.search_posts("artificial intelligence", start_date="2025-01-01")
for tweet in results.data:
    print(tweet.text, tweet.like_count)

client.close()
```

## Authentication

```python
# Pass API key directly
client = XpozClient("your-api-key")

# Or use XPOZ_API_KEY environment variable
import os
os.environ["XPOZ_API_KEY"] = "your-api-key"
client = XpozClient()

# Custom server URL (also reads XPOZ_SERVER_URL env var)
client = XpozClient("your-api-key", server_url="https://xpoz.ai/mcp")

# Custom operation timeout (default: 300 seconds)
client = XpozClient("your-api-key", timeout=600)
```

## Context Manager

```python
# Sync — auto-closes on exit
with XpozClient("your-api-key") as client:
    user = client.twitter.get_user("elonmusk")

# Async
import asyncio
from xpoz import AsyncXpozClient

async def main():
    async with AsyncXpozClient("your-api-key") as client:
        user = await client.twitter.get_user("elonmusk")
        results = await client.twitter.search_posts("AI")
        page2 = await results.next_page()

asyncio.run(main())
```

## Pagination

Methods that return large datasets use server-side pagination (100 items per page). These return a `PaginatedResult[T]` with built-in helpers:

```python
results = client.twitter.search_posts("AI")

results.data                       # list[Tweet] — current page
results.pagination.total_rows      # total matching rows
results.pagination.total_pages     # total pages
results.pagination.page_number     # current page number
results.pagination.page_size       # items per page (100)
results.pagination.results_count   # items on current page
results.has_next_page()            # bool

# Navigate pages
page2 = results.next_page()        # fetch next page
page5 = results.get_page(5)        # jump to specific page

# Fetch everything
all_tweets = results.get_all_pages()  # flat list[Tweet] of all pages

# Export to CSV
csv_url = results.export_csv()     # returns download URL
```

## Field Selection

All methods accept a `fields` parameter. Use snake_case — the SDK translates to camelCase automatically.

```python
# Only fetch the fields you need (faster + less memory)
results = client.twitter.search_posts(
    "AI",
    fields=["id", "text", "like_count", "retweet_count", "created_at_date"]
)

user = client.twitter.get_user(
    "elonmusk",
    fields=["id", "username", "name", "followers_count", "description"]
)
```

Requesting fewer fields significantly improves response time.

## Error Handling

```python
from xpoz import (
    XpozError,
    AuthenticationError,
    ConnectionError,
    OperationTimeoutError,
    OperationFailedError,
    OperationCancelledError,
    NotFoundError,
    ValidationError,
)

try:
    user = client.twitter.get_user("nonexistent_user_12345")
except OperationFailedError as e:
    print(f"Operation {e.operation_id} failed: {e.error}")
except OperationTimeoutError as e:
    print(f"Timed out after {e.elapsed_seconds}s")
except AuthenticationError:
    print("Invalid API key")
except XpozError as e:
    print(f"Xpoz error: {e}")
```

---

## API Reference

### Twitter — `client.twitter`

#### `get_user(identifier, identifier_type="username", *, fields) -> TwitterUser`

Get a single Twitter user profile.

```python
# By username (default)
user = client.twitter.get_user("elonmusk")

# By numeric ID
user = client.twitter.get_user("44196397", identifier_type="id")
```

#### `search_users(name, *, limit=None, fields) -> list[TwitterUser]`

Search users by name or username. Returns up to 10 results.

```python
users = client.twitter.search_users("elon")
```

#### `get_user_connections(username, connection_type, *, fields, force_latest) -> PaginatedResult[TwitterUser]`

Get followers or following for a user.

```python
followers = client.twitter.get_user_connections("elonmusk", "followers")
following = client.twitter.get_user_connections("elonmusk", "following")
```

#### `get_users_by_keywords(query, *, fields, start_date, end_date, language, force_latest) -> PaginatedResult[TwitterUser]`

Find users who authored posts matching a keyword query. Includes aggregation fields like `relevant_tweets_count`, `relevant_tweets_likes_sum`.

```python
users = client.twitter.get_users_by_keywords(
    '"machine learning"',
    fields=["username", "name", "followers_count", "relevant_tweets_count", "relevant_tweets_likes_sum"]
)
```

#### `get_posts_by_ids(post_ids, *, fields, force_latest) -> list[Tweet]`

Get 1-100 posts by their IDs.

```python
tweets = client.twitter.get_posts_by_ids(["1234567890", "0987654321"])
```

#### `get_posts_by_author(identifier, identifier_type="username", *, fields, start_date, end_date, force_latest) -> PaginatedResult[Tweet]`

Get all posts by an author with optional date filtering.

```python
results = client.twitter.get_posts_by_author("elonmusk", start_date="2025-01-01")
```

#### `search_posts(query, *, fields, start_date, end_date, author_username, author_id, language, force_latest) -> PaginatedResult[Tweet]`

Full-text search with filters. Supports exact phrases (`"machine learning"`), boolean operators (`AI AND python`), and parentheses.

```python
results = client.twitter.search_posts(
    '"artificial intelligence" AND ethics',
    start_date="2025-01-01",
    end_date="2025-06-01",
    language="en",
    fields=["id", "text", "like_count", "author_username", "created_at_date"]
)
```

#### `get_retweets(post_id, *, fields, start_date) -> PaginatedResult[Tweet]`

Get retweets of a specific post (database only).

```python
retweets = client.twitter.get_retweets("1234567890")
```

#### `get_quotes(post_id, *, fields, start_date, force_latest) -> PaginatedResult[Tweet]`

Get quote tweets of a specific post.

```python
quotes = client.twitter.get_quotes("1234567890")
```

#### `get_comments(post_id, *, fields, start_date, force_latest) -> PaginatedResult[Tweet]`

Get replies to a specific post.

```python
comments = client.twitter.get_comments("1234567890")
```

#### `get_post_interacting_users(post_id, interaction_type, *, fields, force_latest) -> PaginatedResult[TwitterUser]`

Get users who interacted with a post. `interaction_type`: `"commenters"`, `"quoters"`, `"retweeters"`.

```python
commenters = client.twitter.get_post_interacting_users("1234567890", "commenters")
```

#### `count_posts(phrase, *, start_date, end_date) -> int`

Count tweets containing a phrase within a date range.

```python
count = client.twitter.count_posts("bitcoin", start_date="2025-01-01")
print(f"{count:,} tweets mention bitcoin")
```

---

### Instagram — `client.instagram`

#### `get_user(identifier, identifier_type="username", *, fields) -> InstagramUser`

```python
user = client.instagram.get_user("instagram")
print(f"{user.full_name} — {user.follower_count:,} followers")
```

#### `search_users(name, *, limit=None, fields) -> list[InstagramUser]`

```python
users = client.instagram.search_users("nasa")
```

#### `get_user_connections(username, connection_type, *, fields, force_latest) -> PaginatedResult[InstagramUser]`

```python
followers = client.instagram.get_user_connections("instagram", "followers")
```

#### `get_users_by_keywords(query, *, fields, start_date, end_date, force_latest) -> PaginatedResult[InstagramUser]`

```python
users = client.instagram.get_users_by_keywords('"sustainable fashion"')
```

#### `get_posts_by_ids(post_ids, *, fields, force_latest) -> list[InstagramPost]`

Post IDs must be in strong_id format: `"media_id_user_id"` (e.g. `"3606450040306139062_4836333238"`).

```python
posts = client.instagram.get_posts_by_ids(["3606450040306139062_4836333238"])
```

#### `get_posts_by_user(identifier, identifier_type="username", *, fields, start_date, end_date, force_latest) -> PaginatedResult[InstagramPost]`

```python
results = client.instagram.get_posts_by_user("nasa")
```

#### `search_posts(query, *, fields, start_date, end_date, force_latest) -> PaginatedResult[InstagramPost]`

```python
results = client.instagram.search_posts("travel photography")
```

#### `get_comments(post_id, *, fields, start_date, end_date, force_latest) -> PaginatedResult[InstagramComment]`

```python
comments = client.instagram.get_comments("3606450040306139062_4836333238")
```

#### `get_post_interacting_users(post_id, interaction_type, *, fields, force_latest) -> PaginatedResult[InstagramUser]`

`interaction_type`: `"commenters"`, `"likers"`.

```python
likers = client.instagram.get_post_interacting_users("3606450040306139062_4836333238", "likers")
```

---

### Reddit — `client.reddit`

#### `get_user(username, *, fields) -> RedditUser`

```python
user = client.reddit.get_user("spez")
print(f"{user.username} — {user.total_karma:,} karma")
```

#### `search_users(name, *, limit=None, fields) -> list[RedditUser]`

```python
users = client.reddit.search_users("spez")
```

#### `get_users_by_keywords(query, *, fields, start_date, end_date, subreddit, force_latest) -> PaginatedResult[RedditUser]`

```python
users = client.reddit.get_users_by_keywords('"machine learning"', subreddit="MachineLearning")
```

#### `search_posts(query, *, fields, start_date, end_date, sort, time, subreddit, force_latest) -> PaginatedResult[RedditPost]`

`sort`: `"relevance"`, `"hot"`, `"top"`, `"new"`, `"comments"`. `time`: `"hour"`, `"day"`, `"week"`, `"month"`, `"year"`, `"all"`.

```python
results = client.reddit.search_posts(
    "python tutorial",
    subreddit="learnpython",
    sort="top",
    time="month"
)
```

#### `get_post_with_comments(post_id, *, post_fields, comment_fields, force_latest) -> RedditPostWithComments`

Returns a composite object with the post and its paginated comments.

```python
result = client.reddit.get_post_with_comments("abc123")
print(result.post.title)
for comment in result.comments:
    print(f"  {comment.author_username}: {comment.body[:80]}")
```

#### `search_comments(query, *, fields, start_date, end_date, subreddit) -> PaginatedResult[RedditComment]`

```python
comments = client.reddit.search_comments("helpful tip", subreddit="LifeProTips")
```

#### `search_subreddits(query, *, limit=None, fields) -> list[RedditSubreddit]`

```python
subs = client.reddit.search_subreddits("machine learning")
```

#### `get_subreddit_with_posts(subreddit_name, *, subreddit_fields, post_fields, force_latest) -> SubredditWithPosts`

```python
result = client.reddit.get_subreddit_with_posts("wallstreetbets")
print(f"r/{result.subreddit.display_name} — {result.subreddit.subscribers_count:,} members")
for post in result.posts:
    print(f"  {post.title} ({post.score} points)")
```

#### `get_subreddits_by_keywords(query, *, fields, start_date, end_date, force_latest) -> PaginatedResult[RedditSubreddit]`

```python
subs = client.reddit.get_subreddits_by_keywords("cryptocurrency")
```

---

## Type Models

All models are Pydantic v2 `BaseModel` subclasses with `extra="allow"` (unknown fields are preserved, not rejected). All fields are optional and default to `None`.

### Tweet

| Field                | Type        | Description                |
| -------------------- | ----------- | -------------------------- |
| `id`                 | `str`       | Tweet ID                   |
| `text`               | `str`       | Tweet text content         |
| `author_id`          | `str`       | Author's user ID           |
| `author_username`    | `str`       | Author's username          |
| `like_count`         | `int`       | Number of likes            |
| `retweet_count`      | `int`       | Number of retweets         |
| `reply_count`        | `int`       | Number of replies          |
| `quote_count`        | `int`       | Number of quotes           |
| `impression_count`   | `int`       | Number of impressions      |
| `bookmark_count`     | `int`       | Number of bookmarks        |
| `lang`               | `str`       | Language code              |
| `hashtags`           | `list[str]` | Hashtags in tweet          |
| `mentions`           | `list[str]` | Mentioned usernames        |
| `media_urls`         | `list[str]` | Media attachment URLs      |
| `urls`               | `list[str]` | URLs in tweet              |
| `country`            | `str`       | Country (if geo-tagged)    |
| `created_at`         | `str`       | Creation timestamp         |
| `created_at_date`    | `str`       | Creation date (YYYY-MM-DD) |
| `conversation_id`    | `str`       | Thread conversation ID     |
| `quoted_tweet_id`    | `str`       | ID of quoted tweet         |
| `reply_to_tweet_id`  | `str`       | ID of parent tweet         |
| `is_retweet`         | `bool`      | Whether this is a retweet  |
| `possibly_sensitive` | `bool`      | Sensitive content flag     |

### TwitterUser

| Field                           | Type    | Description                |
| ------------------------------- | ------- | -------------------------- |
| `id`                            | `str`   | User ID                    |
| `username`                      | `str`   | Username (handle)          |
| `name`                          | `str`   | Display name               |
| `description`                   | `str`   | Bio text                   |
| `location`                      | `str`   | Location string            |
| `verified`                      | `bool`  | Verification status        |
| `verified_type`                 | `str`   | Verification type          |
| `followers_count`               | `int`   | Number of followers        |
| `following_count`               | `int`   | Number of following        |
| `tweet_count`                   | `int`   | Total tweets               |
| `likes_count`                   | `int`   | Total likes                |
| `profile_image_url`             | `str`   | Profile picture URL        |
| `created_at`                    | `str`   | Account creation timestamp |
| `account_based_in`              | `str`   | Account location           |
| `is_inauthentic`                | `bool`  | Inauthenticity flag        |
| `is_inauthentic_prob_score`     | `float` | Inauthenticity probability |
| `avg_tweets_per_day_last_month` | `float` | Tweeting frequency         |

### InstagramPost

| Field              | Type  | Description                |
| ------------------ | ----- | -------------------------- |
| `id`               | `str` | Post ID (strong_id format) |
| `caption`          | `str` | Post caption               |
| `username`         | `str` | Author username            |
| `full_name`        | `str` | Author display name        |
| `like_count`       | `int` | Number of likes            |
| `comment_count`    | `int` | Number of comments         |
| `reshare_count`    | `int` | Number of reshares         |
| `video_play_count` | `int` | Video play count           |
| `media_type`       | `str` | Media type                 |
| `image_url`        | `str` | Image URL                  |
| `video_url`        | `str` | Video URL                  |
| `created_at_date`  | `str` | Creation date              |

### InstagramUser

| Field             | Type   | Description         |
| ----------------- | ------ | ------------------- |
| `id`              | `str`  | User ID             |
| `username`        | `str`  | Username            |
| `full_name`       | `str`  | Display name        |
| `biography`       | `str`  | Bio text            |
| `is_private`      | `bool` | Private account     |
| `is_verified`     | `bool` | Verified status     |
| `follower_count`  | `int`  | Followers           |
| `following_count` | `int`  | Following           |
| `media_count`     | `int`  | Total posts         |
| `profile_pic_url` | `str`  | Profile picture URL |

### InstagramComment

| Field                 | Type  | Description     |
| --------------------- | ----- | --------------- |
| `id`                  | `str` | Comment ID      |
| `text`                | `str` | Comment text    |
| `username`            | `str` | Author username |
| `parent_post_id`      | `str` | Parent post ID  |
| `like_count`          | `int` | Number of likes |
| `child_comment_count` | `int` | Reply count     |
| `created_at_date`     | `str` | Creation date   |

### RedditPost

| Field             | Type   | Description           |
| ----------------- | ------ | --------------------- |
| `id`              | `str`  | Post ID               |
| `title`           | `str`  | Post title            |
| `selftext`        | `str`  | Post body text        |
| `author_username` | `str`  | Author username       |
| `subreddit_name`  | `str`  | Subreddit name        |
| `score`           | `int`  | Net score             |
| `upvotes`         | `int`  | Upvote count          |
| `comments_count`  | `int`  | Comment count         |
| `url`             | `str`  | Post URL              |
| `permalink`       | `str`  | Reddit permalink      |
| `is_self`         | `bool` | Self post (text only) |
| `over18`          | `bool` | NSFW flag             |
| `created_at_date` | `str`  | Creation date         |

### RedditUser

| Field                 | Type   | Description           |
| --------------------- | ------ | --------------------- |
| `id`                  | `str`  | User ID               |
| `username`            | `str`  | Username              |
| `total_karma`         | `int`  | Total karma           |
| `link_karma`          | `int`  | Link karma            |
| `comment_karma`       | `int`  | Comment karma         |
| `is_gold`             | `bool` | Reddit Gold status    |
| `is_mod`              | `bool` | Moderator status      |
| `profile_description` | `str`  | Profile bio           |
| `created_at_date`     | `str`  | Account creation date |

### RedditComment

| Field             | Type   | Description     |
| ----------------- | ------ | --------------- |
| `id`              | `str`  | Comment ID      |
| `body`            | `str`  | Comment text    |
| `author_username` | `str`  | Author username |
| `parent_post_id`  | `str`  | Parent post ID  |
| `score`           | `int`  | Net score       |
| `depth`           | `int`  | Nesting depth   |
| `is_submitter`    | `bool` | Is OP           |
| `created_at_date` | `str`  | Creation date   |

### RedditSubreddit

| Field                | Type   | Description       |
| -------------------- | ------ | ----------------- |
| `id`                 | `str`  | Subreddit ID      |
| `display_name`       | `str`  | Subreddit name    |
| `title`              | `str`  | Subreddit title   |
| `public_description` | `str`  | Short description |
| `description`        | `str`  | Full description  |
| `subscribers_count`  | `int`  | Subscriber count  |
| `active_user_count`  | `int`  | Active users      |
| `over18`             | `bool` | NSFW flag         |
| `created_at_date`    | `str`  | Creation date     |

### Composite Types

**`RedditPostWithComments`** — returned by `get_post_with_comments()`:

- `post: RedditPost`
- `comments: list[RedditComment]`
- `comments_pagination: PaginationInfo | None`

**`SubredditWithPosts`** — returned by `get_subreddit_with_posts()`:

- `subreddit: RedditSubreddit`
- `posts: list[RedditPost]`
- `posts_pagination: PaginationInfo | None`

---

## Environment Variables

| Variable          | Description                | Default                   |
| ----------------- | -------------------------- | ------------------------- |
| `XPOZ_API_KEY`    | API key for authentication | —                         |
| `XPOZ_SERVER_URL` | MCP server URL             | `https://mcp.xpoz.ai/mcp` |

## Testing

Tests hit the live Xpoz API and require a valid API key:

```bash
XPOZ_API_KEY=your-api-key pytest tests/ -v
```

Tests must run sequentially in a single process to avoid API rate limiting. Do not run multiple pytest processes in parallel.

## License

MIT
