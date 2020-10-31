import re

from aiohttp import ClientSession


RE_DANBOORU_POST = re.compile(r"^https?://.+?\.donmai\.us/posts/(\d+)")


class BadDanbooruID(Exception):
    pass


def get_post_id(url):
    m = RE_DANBOORU_POST.match(url)

    if m is None:
        return None

    return int(m.group(1))


async def get_post_url(session: ClientSession, post_id: int):
    url = 'https://danbooru.donmai.us/posts/%d.json' % post_id

    async with session.get(url) as response:
        if response.status != 200:
            raise BadDanbooruID(post_id)

        post = await response.json()

        try:
            return post["file_url"]
        except KeyError:
            raise BadDanbooruID(post_id)
