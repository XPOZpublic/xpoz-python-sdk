import json
import sys
from datetime import date

from xpoz._config._tools import (
    TWITTER_TOOLS,
    INSTAGRAM_TOOLS,
    REDDIT_TOOLS,
    TIKTOK_TOOLS,
)
from xpoz.types.twitter import TwitterUser, TwitterPost
from xpoz.types.instagram import InstagramUser, InstagramPost, InstagramComment
from xpoz.types.reddit import RedditUser, RedditPost, RedditComment, RedditSubreddit

try:
    from xpoz.types.tiktok import TiktokUser, TiktokPost, TiktokComment
    HAS_TIKTOK = True
except ImportError:
    HAS_TIKTOK = False


def snake_to_camel(name: str) -> str:
    components = name.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def get_model_fields(model_class) -> list[str]:
    return sorted([snake_to_camel(f) for f in model_class.model_fields.keys()])


def get_all_tool_names(tools_class) -> list[str]:
    names = []
    for attr_name in dir(tools_class):
        if attr_name.startswith("_"):
            continue
        value = getattr(tools_class, attr_name)
        if isinstance(value, str) and not attr_name.startswith("_"):
            names.append(value)
    return sorted(names)


tools = []
for tool_class in [TWITTER_TOOLS, INSTAGRAM_TOOLS, REDDIT_TOOLS, TIKTOK_TOOLS]:
    tools.extend(get_all_tool_names(tool_class))

fields = {
    "twitter.user": get_model_fields(TwitterUser),
    "twitter.tweet": get_model_fields(TwitterPost),
    "instagram.user": get_model_fields(InstagramUser),
    "instagram.post": get_model_fields(InstagramPost),
    "instagram.comment": get_model_fields(InstagramComment),
    "reddit.user": get_model_fields(RedditUser),
    "reddit.post": get_model_fields(RedditPost),
    "reddit.comment": get_model_fields(RedditComment),
    "reddit.subreddit": get_model_fields(RedditSubreddit),
}

if HAS_TIKTOK:
    fields["tiktok.user"] = get_model_fields(TiktokUser)
    fields["tiktok.post"] = get_model_fields(TiktokPost)
    fields["tiktok.comment"] = get_model_fields(TiktokComment)

expectations = {
    "sdk": "xpoz-sdk (Python)",
    "version": "auto-generated",
    "generatedAt": date.today().isoformat(),
    "tools": sorted(set(tools)),
    "fields": fields,
}

json.dump(expectations, sys.stdout, indent=2)
print()
