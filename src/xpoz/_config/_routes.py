DEFAULT_API_URL = "https://api.xpoz.ai"
ENV_API_URL = "XPOZ_API_URL"

INSTAGRAM_BASE = "/api/data/instagram"

INSTAGRAM_LIVE_POSTS = f"{INSTAGRAM_BASE}/posts/live"
INSTAGRAM_LIVE_USER_POSTS = f"{INSTAGRAM_BASE}/posts/users/{{identifier}}/live"
INSTAGRAM_LIVE_POST = f"{INSTAGRAM_BASE}/posts/{{post_id}}/live"
INSTAGRAM_LIVE_POST_COMMENTS = f"{INSTAGRAM_BASE}/posts/{{post_id}}/comments/live"
INSTAGRAM_LIVE_POST_INTERACTING_USERS = (
    f"{INSTAGRAM_BASE}/posts/{{post_id}}/interacting-users/live"
)
INSTAGRAM_LIVE_USERS = f"{INSTAGRAM_BASE}/users/live"
INSTAGRAM_LIVE_USER = f"{INSTAGRAM_BASE}/users/{{identifier}}/live"
INSTAGRAM_LIVE_USER_CONNECTIONS = (
    f"{INSTAGRAM_BASE}/users/{{identifier}}/connections/live"
)
