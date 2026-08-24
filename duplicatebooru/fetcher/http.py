import re

from aiohttp import ClientSession

from .. import __version__
from . import Image, ImageFetchFailed, UnsupportedURL

USER_AGENT = f"duplicatebooru/{__version__}"


async def fetch_http(
    session: ClientSession,
    url: str,
    *,
    ref: str = "",
    original_url: str = "",
    hide_src: bool = False,
    headers: dict | None = None,
) -> Image:
    if re.match(r"^https?://", url) is None:
        raise UnsupportedURL(url)

    if headers:
        headers = headers.copy()
    else:
        headers = {}

    if ref:
        headers["Referer"] = ref

    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            return Image(
                url=original_url or url,
                src=url,
                data=await response.read(),
                hide_src=hide_src,
            )

        raise ImageFetchFailed(response.status, await response.text())
