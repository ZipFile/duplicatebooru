import re
from typing import TypedDict

from aiohttp import ClientSession, encode_basic_auth

from . import Image, ImageFetcher, ImageFetchFailed, UnsupportedURL
from .http import USER_AGENT, fetch_http

RE_DANBOORU_POST = re.compile(r"^https?://.+?\.donmai\.us/posts/(\d+)")


def get_post_id(url: str) -> int | None:
    m = RE_DANBOORU_POST.match(url)

    if m is None:
        return None

    return int(m.group(1))


class Post(TypedDict):
    file_url: str
    is_banned: bool
    is_deleted: bool
    tag_string: str


def should_hide(post: Post) -> bool:
    if post.get("is_banned", False):
        return True
    if post.get("is_deleted", False):
        return True

    tags = set(post["tag_string"].split())

    return bool({"loli", "shota"} & tags)


def fetch_danbooru_post(
    api_key: str = "",
    username: str = "",
    server_url: str = "https://danbooru.donmai.us",
    user_id: int | None = None,
) -> ImageFetcher:
    headers = {
        "User-Agent": make_user_agent(user_id),
    }

    if api_key and username:
        headers["Authorization"] = encode_basic_auth(username, api_key, "utf-8")

    async def fetch(session: ClientSession, url: str) -> Image:
        post_id = get_post_id(url)

        if post_id is None:
            raise UnsupportedURL(url)

        original_url = url
        url = f"{server_url}/posts/{post_id}.json"

        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                raise ImageFetchFailed(f"Failed to get post #{post_id} info")

            post = await response.json()

        try:
            url = post["file_url"]
        except KeyError:
            raise ImageFetchFailed(f"Post #{post_id} has no image url")

        return await fetch_http(
            session,
            url,
            original_url=original_url,
            hide_src=should_hide(post),
            headers=headers,
        )

    return fetch


def make_user_agent(user_id: int | None = None) -> str:
    if user_id:
        return f"{USER_AGENT}; user #{user_id}"
    return USER_AGENT
