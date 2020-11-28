from dataclasses import dataclass
from typing import Any

from aiohttp import ClientSession

from .cache import Cache
from .fetcher import ImageFetcher
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


async def process(
    session: ClientSession,
    url: str,
    fetch: ImageFetcher,
    cache: Cache,
) -> Info:
    cached_info = await cache.get(url)

    if cached_info:
        info = cached_info
        src = info['__src']
        info['__from_cache'] = True
    else:
        image = await fetch(session, url)

        info = await get_info(image.data)
        info = info[0]["image"]
        info['__src'] = src = image.src

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
