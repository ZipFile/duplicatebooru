from dataclasses import dataclass
from typing import Sequence

from aiohttp import ClientSession

from typing_extensions import Protocol


@dataclass
class Image:
    url: str
    src: str = ''
    data: bytes = b''


class UnsupportedURL(Exception):
    pass


class ImageFetchFailed(Exception):
    pass


class ImageFetcher(Protocol):
    async def __call__(self, session: ClientSession, url: str) -> Image:
        """Fetch image from the url.

        Raises:
            UnsupportedURL: if given url is not supported.
            ImageFetchFailed: when failed to download an image.

        Returns:
            Image instance.
        """


def try_fetcher(fetchers: Sequence[ImageFetcher]) -> ImageFetcher:
    """Return url fetcher iterating over list of fetchers until success."""

    async def fetch(session: ClientSession, url: str) -> Image:
        for fetch in fetchers:
            try:
                return await fetch(session, url)
            except UnsupportedURL:
                pass

        raise UnsupportedURL(url)

    return fetch
