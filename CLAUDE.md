# CLAUDE.md

This file provides guidance to Claude Code when working with the xpoz-sdk repository.

## Project Overview

Monorepo for Xpoz SDK — client libraries that wrap the xpoz-mcp server (MCP protocol) into simple, idiomatic APIs. Currently contains a Python SDK; TypeScript is planned.

## Repository Structure

```
xpoz-sdk/
├── python/                     # Python SDK (PyPI: xpoz)
│   ├── pyproject.toml          # Package config (hatchling build system)
│   ├── README.md               # Python-specific documentation
│   └── src/xpoz/               # Package source
│       ├── __init__.py          # Public exports
│       ├── _version.py          # Version string
│       ├── _client.py           # XpozClient (sync)
│       ├── _async_client.py     # AsyncXpozClient (async)
│       ├── _transport.py        # MCP Streamable HTTP transport wrapper
│       ├── _polling.py          # Operation polling (5s interval, configurable timeout)
│       ├── _pagination.py       # PaginatedResult[T] + AsyncPaginatedResult[T]
│       ├── _field_mapping.py    # snake_case <-> camelCase bidirectional mapping
│       ├── _exceptions.py       # Error hierarchy
│       ├── types/               # Pydantic v2 models
│       │   ├── __init__.py
│       │   ├── common.py        # PaginationInfo
│       │   ├── twitter.py       # Tweet, TwitterUser
│       │   ├── instagram.py     # InstagramPost, InstagramUser, InstagramComment
│       │   └── reddit.py        # RedditPost, RedditUser, RedditComment, RedditSubreddit, composites
│       └── namespaces/          # Platform method groups (sync + async variants)
│           ├── __init__.py
│           ├── _base.py         # BaseNamespace, AsyncBaseNamespace (shared logic)
│           ├── twitter.py       # TwitterNamespace (12 methods)
│           ├── instagram.py     # InstagramNamespace (9 methods)
│           └── reddit.py        # RedditNamespace (9 methods)
└── typescript/                  # Planned TypeScript SDK
```

## Development Commands

All commands run from `python/` directory. Requires a Python 3.10+ venv.

```bash
# Create venv and install in editable mode
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Type checking
pip install mypy
mypy src/xpoz/ --ignore-missing-imports

# Verify imports
python3 -c "from xpoz import XpozClient, AsyncXpozClient; print('OK')"
```

## Testing

All commands run from `python/` directory.

```bash
XPOZ_API_KEY=... pytest tests/ -v
```

Tests hit the live Xpoz API and must run in a **single sequential process** — do not run multiple pytest processes in parallel. The Xpoz API rate-limits concurrent connections, causing operations to queue beyond the timeout and cascade failures through the module-scoped client.

The pytest timeout (660s in `pyproject.toml`) is intentionally higher than the client polling timeout (600s in `conftest.py`) so the SDK raises a clean `OperationTimeoutError` instead of pytest killing the process via signal (which breaks the shared client and cascades failures to all subsequent tests).

## Architecture

### Transport Layer (`_transport.py`)

- `McpTransport` (async): Wraps MCP Python SDK's `streamablehttp_client` + `ClientSession`. Injects API key as Bearer token. Exposes `call_tool(name, args) -> dict`.
- `SyncTransport`: Runs `McpTransport` on an anyio `BlockingPortal` background thread for synchronous usage.

### Operation Polling (`_polling.py`)

Many xpoz-mcp tools return an `operationId` instead of immediate results (long-running queries). The poller:
- Calls `checkOperationStatus` every 5 seconds
- Returns result dict on `completed` status (or if `results`/`downloadUrl` present)
- Raises `OperationFailedError` / `OperationCancelledError` / `OperationTimeoutError`
- Default timeout: 300 seconds (configurable via `XpozClient(timeout=N)`)

### Pagination (`_pagination.py`)

- `PaginatedResult[T]` (sync) and `AsyncPaginatedResult[T]` (async)
- Wraps first-page data + `PaginationInfo` + a stored `fetch_page` callback
- `next_page()`, `get_page(n)`, `get_all_pages()` fetch subsequent pages using `tableName` from first response
- `export_csv()` polls the export operation and returns a download URL

### Field Mapping (`_field_mapping.py`)

- Users pass snake_case field names (Pythonic)
- SDK converts to camelCase for MCP wire format
- Responses are mapped back to snake_case before Pydantic validation
- `camel_to_snake("likeCount")` -> `"like_count"`
- `snake_to_camel("like_count")` -> `"likeCount"`

### Namespace Pattern

Each platform (Twitter, Instagram, Reddit) has sync + async namespace classes:
- Sync: `TwitterNamespace(BaseNamespace)` — methods call `self._call_and_maybe_poll()` which handles operationId polling transparently
- Async: `AsyncTwitterNamespace(AsyncBaseNamespace)` — same but with `await`
- Both inherit `_build_args()` (filters None values), `_convert_fields()` (snake->camel), `_build_paginated_result()`

### Client Classes

- `XpozClient`: Creates `SyncTransport`, connects immediately in `__init__`, attaches sync namespaces. Supports context manager (`with`).
- `AsyncXpozClient`: Creates `McpTransport`, connects in `connect()` or `__aenter__`. Supports async context manager (`async with`).

## Type Models

All Pydantic models use `extra="allow"` — unknown fields from the API are preserved, not rejected. All fields are `Optional` with `None` default (the API returns only requested fields).

## Relationship to xpoz-mcp

This SDK is a client for the xpoz-mcp server. Key correspondences:

| SDK Concept | xpoz-mcp Source |
|---|---|
| Tool names | `src/consts/tools.consts.ts` |
| Tweet fields | `src/entities/twitter/Tweet.ts` |
| TwitterUser fields | `src/entities/twitter/User.ts` |
| InstagramPost fields | `src/entities/instagram/Post.ts` |
| InstagramUser fields | `src/entities/instagram/User.ts` |
| InstagramComment fields | `src/entities/instagram/Comment.ts` |
| RedditPost fields | `src/entities/reddit/Post.ts` |
| RedditUser fields | `src/entities/reddit/User.ts` |
| RedditComment fields | `src/entities/reddit/Comment.ts` |
| RedditSubreddit fields | `src/entities/reddit/Subreddit.ts` |
| Input schemas | `src/schemas/twitter/`, `src/schemas/instagram/`, `src/schemas/reddit/` |
| Operation protocol | `src/tools/operations.ts` |

When xpoz-mcp adds new fields or tools, the SDK should be updated to match.

## MCP Tool Name Mapping

| SDK Method | MCP Tool |
|---|---|
| `twitter.get_posts_by_ids()` | `getTwitterPostsByIds` |
| `twitter.get_posts_by_author()` | `getTwitterPostsByAuthor` |
| `twitter.search_posts()` | `getTwitterPostsByKeywords` |
| `twitter.get_retweets()` | `getTwitterPostRetweets` |
| `twitter.get_quotes()` | `getTwitterPostQuotes` |
| `twitter.get_comments()` | `getTwitterPostComments` |
| `twitter.get_post_interacting_users()` | `getTwitterPostInteractingUsers` |
| `twitter.count_posts()` | `countTweets` |
| `twitter.get_user()` | `getTwitterUser` |
| `twitter.search_users()` | `searchTwitterUsers` |
| `twitter.get_user_connections()` | `getTwitterUserConnections` |
| `twitter.get_users_by_keywords()` | `getTwitterUsersByKeywords` |
| `instagram.get_posts_by_ids()` | `getInstagramPostsByIds` |
| `instagram.get_posts_by_user()` | `getInstagramPostsByUser` |
| `instagram.search_posts()` | `getInstagramPostsByKeywords` |
| `instagram.get_comments()` | `getInstagramCommentsByPostId` |
| `instagram.get_user()` | `getInstagramUser` |
| `instagram.search_users()` | `searchInstagramUsers` |
| `instagram.get_user_connections()` | `getInstagramUserConnections` |
| `instagram.get_post_interacting_users()` | `getInstagramPostInteractingUsers` |
| `instagram.get_users_by_keywords()` | `getInstagramUsersByKeywords` |
| `reddit.search_posts()` | `getRedditPostsByKeywords` |
| `reddit.get_post_with_comments()` | `getRedditPostWithCommentsById` |
| `reddit.search_comments()` | `getRedditCommentsByKeywords` |
| `reddit.get_user()` | `getRedditUser` |
| `reddit.search_users()` | `searchRedditUsers` |
| `reddit.get_users_by_keywords()` | `getRedditUsersByKeywords` |
| `reddit.search_subreddits()` | `searchRedditSubreddits` |
| `reddit.get_subreddit_with_posts()` | `getRedditSubredditWithPostsByName` |
| `reddit.get_subreddits_by_keywords()` | `getRedditSubredditsByKeywords` |

## Conventions

- Python code uses snake_case for all public APIs
- Private/internal modules are prefixed with `_` (e.g., `_transport.py`)
- All Pydantic models live in `types/` — never define models in namespace or client files
- No inline comments in code — write self-documenting code with clear names
- All fields optional with `None` default (API returns only requested fields)
- `extra="allow"` on all models to handle new API fields gracefully
- Use `typing.Any` sparingly — prefer specific types where possible
- Dates passed as `str` in `YYYY-MM-DD` format (matching xpoz-mcp)
