import re

from aiohttp import ClientSession

from . import Image, ImageFetchFailed, UnsupportedURL


async def fetch_http(
    session: ClientSession, url: str, *,
    ref: str = '',
    original_url: str = '',
) -> Image:
    if re.match(r"^https?://", url) is None:
        raise UnsupportedURL(url)

    headers = {}

    if ref:
        headers["Referer"] = ref

    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            return Image(original_url or url, url, await response.read())

        raise ImageFetchFailed(response.status, await response.text())
