"""Derive per-method allowed-fields lists from the live API.

For every namespace method that takes a `fields=` (or `*_fields=`) parameter:
1. Look up the result model's `model_fields` (the union — superset of what
   the API will accept).
2. Call the method with that union as `fields=`.
3. Parse the API's "Allowed fields: ..." rejection (if any) to capture the
   true accepted set. If the API doesn't reject, every model field is allowed.

Output: a Python module written to src/xpoz/_config/_allowed_fields.py with
constants per tool name (matching the existing _tools.py style), plus a
SimpleNamespace bundle.

Run from repo root with API key set:
    XPOZ_API_KEY=... python scripts/derive_allowed_fields.py
"""
from __future__ import annotations

import inspect
import re
import sys
import typing
from collections import defaultdict
from pathlib import Path

from xpoz import XpozClient
from xpoz._config import _tools
from xpoz.namespaces._base import BaseNamespace
from xpoz.namespaces import (
    TwitterNamespace, InstagramNamespace, RedditNamespace,
    TiktokNamespace, TrackingNamespace,
)

# Map a method on a namespace class to the tool name it calls. We discover this
# by reading the method body — every namespace method calls
# self._call_and_maybe_poll(_tools.X, args), so we grep for that.
TOOL_REF_RE = re.compile(r"_tools\.([A-Z_]+)")

PLATFORMS = {
    "twitter":   TwitterNamespace,
    "instagram": InstagramNamespace,
    "reddit":    RedditNamespace,
    "tiktok":    TiktokNamespace,
    "tracking":  TrackingNamespace,
}

# Sample call args per (platform, method). Picked to be cheap, well-known
# identifiers that won't change. Keep limit small — we only need enough rows
# to trigger the field validation, not full results.
def discover_real_ids(client) -> dict[str, str]:
    """Fetch one real post ID per platform via a search call so the *_by_ids
    and comment probes use IDs that actually exist."""
    ids: dict[str, str] = {}
    try:
        ids["twitter"] = client.twitter.search_posts("bitcoin", limit=1).data[0].id
    except Exception as e:
        print(f"  ! couldn't get twitter post id: {e}")
    try:
        ids["instagram"] = client.instagram.search_posts("travel", limit=1).data[0].id
    except Exception as e:
        print(f"  ! couldn't get instagram post id: {e}")
    try:
        ids["reddit"] = client.reddit.search_posts("python", limit=1).data[0].id
    except Exception as e:
        print(f"  ! couldn't get reddit post id: {e}")
    try:
        ids["tiktok"] = client.tiktok.search_posts("dance", limit=1).data[0].id
    except Exception as e:
        print(f"  ! couldn't get tiktok post id: {e}")
    return ids


def build_probe_args(real_ids: dict[str, str]) -> dict[tuple[str, str], dict]:
    return {
        ("twitter", "get_user"):                 dict(identifier="elonmusk"),
        ("twitter", "get_users"):                dict(identifiers=["elonmusk"]),
        ("twitter", "search_users"):             dict(name="elon", limit=1),
        ("twitter", "get_users_by_keywords"):    dict(query='"machine learning"', limit=1),
        ("twitter", "get_user_connections"):     dict(username="elonmusk", connection_type="followers"),
        ("twitter", "search_posts"):             dict(query="bitcoin", limit=1),
        ("twitter", "get_posts_by_author"):      dict(identifier="elonmusk", limit=1),
        ("twitter", "get_posts_by_ids"):         dict(post_ids=[real_ids["twitter"]]) if "twitter" in real_ids else None,
        ("twitter", "get_comments"):             dict(post_id=real_ids["twitter"]) if "twitter" in real_ids else None,
        ("twitter", "get_quotes"):               dict(post_id=real_ids["twitter"]) if "twitter" in real_ids else None,
        ("twitter", "get_retweets"):             dict(post_id=real_ids["twitter"]) if "twitter" in real_ids else None,
        ("twitter", "get_post_interacting_users"): dict(post_id=real_ids["twitter"], interaction_type="commenters") if "twitter" in real_ids else None,

        ("instagram", "get_user"):              dict(identifier="instagram"),
        ("instagram", "search_users"):          dict(name="instagram", limit=1),
        ("instagram", "get_users_by_keywords"): dict(query="travel", limit=1),
        ("instagram", "get_user_connections"):  dict(username="instagram", connection_type="followers"),
        ("instagram", "search_posts"):          dict(query="travel", limit=1),
        ("instagram", "get_posts_by_user"):     dict(identifier="instagram", limit=1),
        ("instagram", "get_posts_by_ids"):      dict(post_ids=[real_ids["instagram"]]) if "instagram" in real_ids else None,
        ("instagram", "get_comments"):          dict(post_id=real_ids["instagram"]) if "instagram" in real_ids else None,
        ("instagram", "get_post_interacting_users"): dict(post_id=real_ids["instagram"], interaction_type="commenters") if "instagram" in real_ids else None,

        ("reddit", "get_user"):                  dict(username="spez"),
        ("reddit", "search_users"):              dict(name="spez", limit=1),
        ("reddit", "get_users_by_keywords"):     dict(query="python"),  # no `limit` kwarg
        ("reddit", "search_posts"):              dict(query="python", limit=1),
        ("reddit", "search_comments"):           dict(query="python"),
        ("reddit", "search_subreddits"):         dict(query="python", limit=1),
        ("reddit", "get_subreddits_by_keywords"): dict(query="python"),
        ("reddit", "get_post_with_comments"):    dict(post_id=real_ids["reddit"]) if "reddit" in real_ids else None,
        ("reddit", "get_subreddit_with_posts"):  dict(subreddit_name="python"),

        ("tiktok", "get_user"):                  dict(identifier="tiktok"),
        ("tiktok", "search_users"):              dict(name="tiktok", limit=1),
        ("tiktok", "get_users_by_keywords"):     dict(query="dance", limit=1),
        ("tiktok", "search_posts"):              dict(query="dance", limit=1),
        ("tiktok", "get_posts_by_user"):         dict(identifier="tiktok", limit=1),
        ("tiktok", "get_posts_by_ids"):          dict(post_ids=[real_ids["tiktok"]]) if "tiktok" in real_ids else None,
        ("tiktok", "get_comments"):              dict(post_id=real_ids["tiktok"]) if "tiktok" in real_ids else None,
    }


PROBE_ARGS: dict[tuple[str, str], dict] = {}  # populated at runtime

INVALID_RE = re.compile(r"Invalid field\(s\):\s*([^.|]+)")


def camel_to_snake(s: str) -> str:
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", s)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s).lower()


def flatten_exc(e: BaseException) -> str:
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


def find_tool_name(method) -> str | None:
    """Read the method source and find which _tools.X it references."""
    try:
        src = inspect.getsource(method)
    except (TypeError, OSError):
        return None
    m = TOOL_REF_RE.search(src)
    return m.group(1) if m else None


def get_inner_model(ann):
    while ann is not None:
        origin = typing.get_origin(ann)
        if origin is None:
            return ann if hasattr(ann, "model_fields") else None
        args = typing.get_args(ann)
        if not args:
            return origin if hasattr(origin, "model_fields") else None
        ann = args[0]
    return None


def fields_params_for(method) -> dict[str, type]:
    """Return mapping of {param_name: result_model} for each *_fields param."""
    sig = inspect.signature(method)
    hints = typing.get_type_hints(method)
    return_ann = hints.get("return")
    inner = get_inner_model(return_ann)
    out = {}
    for pname in sig.parameters:
        if pname == "self":
            continue
        if pname != "fields" and not pname.endswith("_fields"):
            continue
        if pname == "fields":
            model = inner
        else:
            stem = pname[: -len("_fields")]
            if inner is None:
                model = None
            else:
                model = None
                for cand in (stem, stem + "s"):
                    f = inner.model_fields.get(cand) if hasattr(inner, "model_fields") else None
                    if f is not None:
                        model = get_inner_model(f.annotation)
                        if model is not None:
                            break
        if model is None or not hasattr(model, "model_fields"):
            continue
        out[pname] = model
    return out


def probe(client, ns_name, method_name) -> dict[str, frozenset[str]] | None:
    """Probe one method. Returns {param_name: frozenset[snake_case allowed]}."""
    ns = getattr(client, ns_name)
    method = getattr(ns, method_name, None)
    if method is None:
        return None
    fp = fields_params_for(method)
    if not fp:
        return None

    base_args = PROBE_ARGS.get((ns_name, method_name))
    if base_args is None:
        print(f"  ! {ns_name}.{method_name}: no probe args (real ID unavailable) — skipping")
        return None

    allowed_per_param: dict[str, frozenset[str]] = {}
    for pname, model in fp.items():
        union = list(model.model_fields)
        try:
            method(**base_args, **{pname: union})
            # No rejection — every field accepted
            allowed_per_param[pname] = frozenset(union)
        except BaseException as e:
            msg = flatten_exc(e)
            m = INVALID_RE.search(msg)
            if m:
                rejected_camel = [s.strip() for s in m.group(1).split(",") if s.strip()]
                rejected = {camel_to_snake(s) for s in rejected_camel}
                accepted = frozenset(f for f in union if f not in rejected)
                allowed_per_param[pname] = accepted
            elif "validation error" in msg.lower():
                # SDK type-mismatch on response parsing. The API ACCEPTED the
                # request (otherwise we'd have seen "Invalid field(s)" first),
                # so every field we passed is allowed. Fallback is correct.
                print(f"  ⚠ {ns_name}.{method_name}.{pname}: SDK type-mismatch on response (API accepted all fields); using model_fields")
                allowed_per_param[pname] = frozenset(union)
            else:
                # Probe failed before reaching field-validation (e.g. invalid
                # ID, server error). We don't know what's accepted, so omit
                # this param rather than guess. Caller can re-probe later.
                print(f"  ✗ {ns_name}.{method_name}.{pname}: probe failed before field validation: {msg[:200]}")
                # Don't add to allowed_per_param — leave it omitted.
    return allowed_per_param if allowed_per_param else None


def main() -> int:
    global PROBE_ARGS
    client = XpozClient()
    print("=== discovering real IDs per platform ===")
    real_ids = discover_real_ids(client)
    for k, v in real_ids.items():
        print(f"  {k}: {v}")
    PROBE_ARGS = build_probe_args(real_ids)
    PROBE_ARGS = {k: v for k, v in PROBE_ARGS.items() if v is not None}

    results: dict[str, dict[str, frozenset[str]]] = {}
    method_to_tool: dict[str, str] = {}

    for ns_name, ns_cls in PLATFORMS.items():
        if ns_cls is TrackingNamespace:
            continue  # tracking has no fields= params on its methods
        print(f"\n=== {ns_name} ===")
        for method_name in sorted(dir(ns_cls)):
            if method_name.startswith("_"):
                continue
            method = getattr(ns_cls, method_name)
            if not callable(method):
                continue
            tool = find_tool_name(method)
            if tool is None:
                continue
            print(f"  probe {ns_name}.{method_name} → {tool}")
            allowed = probe(client, ns_name, method_name)
            if allowed is not None:
                results[tool] = allowed
                method_to_tool[f"{ns_name}.{method_name}"] = tool

    client.close()

    # Render the constants module
    out_path = Path(__file__).parent.parent / "src" / "xpoz" / "_config" / "_allowed_fields.py"
    lines = [
        '"""Per-method allowed-fields metadata, derived empirically from the live API.',
        "",
        "Each constant is a frozenset of field names (snake_case) that the API",
        "accepts in the corresponding tool's `fields=` parameter. For methods that",
        "expose nested *_fields params (e.g. Reddit's get_post_with_comments), the",
        "constants are suffixed with the param name.",
        "",
        "Regenerate with: scripts/derive_allowed_fields.py",
        '"""',
        "from __future__ import annotations",
        "",
        "from types import SimpleNamespace",
        "",
        "",
    ]
    by_const_name: dict[str, frozenset[str]] = {}
    for tool, per_param in sorted(results.items()):
        for pname, fields in per_param.items():
            const_name = tool + ("_FIELDS" if pname == "fields" else f"_{pname.upper()}")
            by_const_name[const_name] = fields

    for const_name in sorted(by_const_name):
        fields = sorted(by_const_name[const_name])
        if not fields:
            lines.append(f"{const_name}: frozenset[str] = frozenset()")
        else:
            lines.append(f"{const_name}: frozenset[str] = frozenset({{")
            for f in fields:
                lines.append(f'    "{f}",')
            lines.append("})")
        lines.append("")

    lines.append("")
    lines.append("ALLOWED_FIELDS = SimpleNamespace(")
    for const_name in sorted(by_const_name):
        lines.append(f"    {const_name}={const_name},")
    lines.append(")")
    lines.append("")

    out_path.write_text("\n".join(lines))
    print(f"\nWrote {out_path} ({len(by_const_name)} constants)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
