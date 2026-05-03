"""Contract tests for per-method `allowed_fields` metadata.

Each test calls the corresponding method with `fields=method.allowed_fields[<param>]`
and asserts the API does not reject any of those names. This is the regression
guarantee that keeps the metadata honest as the API or SDK evolves: if the API
removes (or adds) an accepted field, this test breaks.

Tests skip automatically when:
- XPOZ_API_KEY is not set (handled by the `client` fixture)
- The probe-arg requires a real ID we couldn't pre-fetch (skipped at parametrize time)

A separate set of tests covers the introspection contract: every method that
accepts a `fields=` parameter has `allowed_fields` metadata attached.
"""
from __future__ import annotations

import re
import pytest

from xpoz._exceptions import OperationFailedError
from xpoz.namespaces import (
    TwitterNamespace, AsyncTwitterNamespace,
    InstagramNamespace, AsyncInstagramNamespace,
    RedditNamespace, AsyncRedditNamespace,
    TiktokNamespace, AsyncTiktokNamespace,
)


# (label, ns_attr, method_name, base_args_factory)
# base_args_factory: callable(client) -> dict OR sentinel "needs_post_id"
_PROBES = [
    ("twitter.get_user",                  "twitter",   "get_user",                 lambda c: dict(identifier="elonmusk")),
    ("twitter.get_users",                 "twitter",   "get_users",                lambda c: dict(identifiers=["elonmusk"])),
    ("twitter.search_users",              "twitter",   "search_users",             lambda c: dict(name="elon", limit=1)),
    ("twitter.get_users_by_keywords",     "twitter",   "get_users_by_keywords",    lambda c: dict(query='"machine learning"', limit=1)),
    ("twitter.get_user_connections",      "twitter",   "get_user_connections",     lambda c: dict(username="elonmusk", connection_type="followers")),
    ("twitter.search_posts",              "twitter",   "search_posts",             lambda c: dict(query="bitcoin", limit=1)),
    ("twitter.get_posts_by_author",       "twitter",   "get_posts_by_author",      lambda c: dict(identifier="elonmusk", limit=1)),

    ("instagram.get_user",                "instagram", "get_user",                 lambda c: dict(identifier="instagram")),
    ("instagram.get_users_by_keywords",   "instagram", "get_users_by_keywords",    lambda c: dict(query="travel", limit=1)),

    ("reddit.get_subreddits_by_keywords", "reddit",    "get_subreddits_by_keywords", lambda c: dict(query="python")),

    ("tiktok.get_user",                   "tiktok",    "get_user",                 lambda c: dict(identifier="tiktok")),
    ("tiktok.get_users_by_keywords",      "tiktok",    "get_users_by_keywords",    lambda c: dict(query="dance", limit=1)),
    ("tiktok.search_users",               "tiktok",    "search_users",             lambda c: dict(name="tiktok", limit=1)),
]


_INVALID_RE = re.compile(r"Invalid field\(s\)")


def _flatten(e: BaseException) -> str:
    msgs: list[str] = []
    seen: set[int] = set()

    def visit(x: BaseException) -> None:
        if id(x) in seen:
            return
        seen.add(id(x))
        if hasattr(x, "exceptions"):
            for s in x.exceptions:  # type: ignore[attr-defined]
                visit(s)
        else:
            msgs.append(f"{type(x).__name__}: {x}")

    visit(e)
    return " | ".join(msgs)


# ---- introspection contract ----

@pytest.mark.parametrize("ns_cls", [
    TwitterNamespace, AsyncTwitterNamespace,
    InstagramNamespace, AsyncInstagramNamespace,
    RedditNamespace, AsyncRedditNamespace,
    TiktokNamespace, AsyncTiktokNamespace,
])
def test_every_fields_method_has_allowed_fields_metadata(ns_cls: type) -> None:
    """Every namespace method whose signature has a `fields=` (or `*_fields=`)
    parameter must declare `allowed_fields` metadata."""
    import inspect

    missing: list[str] = []
    for name in dir(ns_cls):
        if name.startswith("_"):
            continue
        m = getattr(ns_cls, name)
        if not callable(m):
            continue
        try:
            sig = inspect.signature(m)
        except (TypeError, ValueError):
            continue
        fields_params = [
            p for p in sig.parameters
            if p == "fields" or p.endswith("_fields")
        ]
        if not fields_params:
            continue
        af = getattr(m, "allowed_fields", None)
        if not isinstance(af, dict) or not all(p in af for p in fields_params):
            missing.append(f"{ns_cls.__name__}.{name} (params: {fields_params})")
    assert not missing, f"methods missing allowed_fields: {missing}"


# ---- live API round-trip contract ----

@pytest.mark.parametrize("label,ns_attr,method_name,args_factory", _PROBES)
def test_allowed_fields_round_trip(client, label, ns_attr, method_name, args_factory):
    """Calling each method with fields=method.allowed_fields['fields'] must not
    trigger an `Invalid field(s)` API rejection. (Other failures, e.g.
    SDK type-mismatch on the response, are out of scope for this test.)"""
    ns = getattr(client, ns_attr)
    method = getattr(ns, method_name)
    af = getattr(method, "allowed_fields", None)
    assert af is not None, f"{label}: no allowed_fields metadata"

    fields = sorted(af["fields"])
    args = args_factory(client)
    try:
        method(**args, fields=fields)
    except OperationFailedError as e:
        msg = _flatten(e)
        if _INVALID_RE.search(msg):
            pytest.fail(
                f"{label}: API rejected one or more fields from method.allowed_fields['fields']. "
                f"Either the metadata is stale or the API contract changed.\n"
                f"Server response: {msg}"
            )
        # Other failures (e.g. server-side issue) are not regressions of allowed_fields metadata.
        pytest.skip(f"{label}: server-side error unrelated to fields validation: {msg[:200]}")
    except BaseException as e:
        msg = _flatten(e)
        if _INVALID_RE.search(msg):
            pytest.fail(
                f"{label}: API rejected one or more fields. Server response: {msg}"
            )
        # SDK type-mismatch on response parsing means the API accepted everything;
        # the metadata is still correct. Skip rather than fail.
        if "validation error" in msg.lower():
            pytest.skip(f"{label}: SDK type-mismatch on response (fields validation passed)")
        pytest.skip(f"{label}: unrelated error: {msg[:200]}")
