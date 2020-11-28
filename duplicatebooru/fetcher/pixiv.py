import re

from aiohttp import ClientSession

from . import Image, UnsupportedURL
from .http import fetch_http


async def fetch_pixiv_url(session: ClientSession, url: str) -> Image:
    if re.match(r"^https?://i.pximg.net/", url) is None:
        raise UnsupportedURL(url)

    return await fetch_http(session, url, ref="https://www.pixiv.net/")
