from dataclasses import dataclass
from typing import Any

from aiohttp import ClientSession

from .cache import Cache
from .danbooru import get_post_id, get_post_url
from .imagemagick import get_info


@dataclass
class Info:
    url: str
    src: str = ''
    width: int = 0
    height: int = 0
    format: str = ''
    hash: str = ''
    dupe: bool = False
    magick: Any = None
    error: str = ''


class NotAURL(Exception):
    pass


class ImageFetchFailed(Exception):
    pass


async def normalize_image_url(session: ClientSession, url: str) -> str:
    if not (url.startswith("https://") or url.startswith("http://")):
        raise NotAURL(url)

    post_id = get_post_id(url)

    if post_id is None:
        return url

    return await get_post_url(session, post_id)


async def fetch_image(session: ClientSession, url: str) -> bytes:
    src = await normalize_image_url(session, url)

    async with session.get(src) as response:
        if response.status == 200:
            return url, src, await response.read()

        raise ImageFetchFailed(response.status, await response.text())


async def process(session: ClientSession, url: str, cache: Cache) -> Info:
    cached_info = await cache.get(url)

    if cached_info:
        info = cached_info
        src = info['__src']
        info['__from_cache'] = True
    else:
        url, src, image = await fetch_image(session, url)

        info = await get_info(image)
        info = info[0]["image"]
        info['__src'] = src

        await cache.set(url, info)
        info['__from_cache'] = False

    return Info(
        url=url,
        src=src,
        width=info["geometry"]["width"],
        height=info["geometry"]["height"],
        format=info["format"],
        hash=info["properties"]["signature"],
        magick=info,
    )
