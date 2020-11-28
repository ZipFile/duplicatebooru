import re
from typing import Optional

from aiohttp import BasicAuth, ClientSession

from . import Image, ImageFetchFailed, ImageFetcher, UnsupportedURL
from .http import fetch_http


RE_DANBOORU_POST = re.compile(r"^https?://.+?\.donmai\.us/posts/(\d+)")


def get_post_id(url: str) -> Optional[int]:
    m = RE_DANBOORU_POST.match(url)

    if m is None:
        return None

    return int(m.group(1))


def fetch_danbooru_post(
    api_key: str = '',
    username: str = '',
    server_url: str = 'https://danbooru.donmai.us',
) -> ImageFetcher:
    auth: Optional[BasicAuth]

    if api_key and username:
        auth = BasicAuth(username, api_key, 'utf-8')
    else:
        auth = None

    async def fetch(session: ClientSession, url: str) -> Image:
        post_id = get_post_id(url)

        if post_id is None:
            raise UnsupportedURL(url)

        original_url = url
        url = f'{server_url}/posts/{post_id}.json'

        async with session.get(url, auth=auth) as response:
            if response.status != 200:
                raise ImageFetchFailed(f"Failed to get post #{post_id} info")

            post = await response.json()

        try:
            url = post["file_url"]
        except KeyError:
            raise ImageFetchFailed(f"Post #{post_id} has no image url")

        return await fetch_http(session, url, original_url=original_url)

    return fetch
