import logging
import os
from distutils.util import strtobool
from typing import Any, Callable, MutableMapping, Optional

from aiohttp.web import Application, run_app, static

from aiohttp_jinja2 import setup as setup_aiohttp_jinja2

from aioredis import create_redis_pool

from jinja2 import FileSystemLoader

from .cache import MemoryCache, RedisCache
from .fetcher import try_fetcher
from .fetcher.danbooru import fetch_danbooru_post
from .fetcher.http import fetch_http
from .fetcher.pixiv import fetch_pixiv_url
from .web import routes


async def setup_aioredis(redis_url: str, app: Application) -> None:
    redis = await create_redis_pool(redis_url)
    app['redis'] = redis
    app['cache'] = RedisCache(redis)


async def teardown_aioredis(app: Application) -> None:
    redis = app['redis']

    redis.close()
    await redis.wait_closed()

    del app['cache']
    del app['redis']


def maybe_set(
    settings: MutableMapping[str, Any],
    name: str,
    envvar: str,
    coercer: Optional[Callable[[str], Any]] = None,
    default: Any = None,
) -> None:
    if envvar in os.environ:
        value = os.environ[envvar]

        if coercer is not None:
            value = coercer(value)

        settings.setdefault(name, value)
    elif default is not None:
        settings.setdefault(name, default)


def main(debug: bool = True) -> None:
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    app = Application()

    setup_aiohttp_jinja2(
        app,
        loader=FileSystemLoader(os.path.dirname(__file__)),
    )

    maybe_set(app, 'debug', 'DEBUG', strtobool, debug)
    maybe_set(app, 'redis_url', 'REDIS_URL', default='')
    maybe_set(app, 'port', 'PORT', int, 8080)
    maybe_set(app, 'danbooru_api_key', 'DANBOORU_API_KEY', default='')
    maybe_set(app, 'danbooru_username', 'DANBOORU_USERNAME', default='')

    static_path = os.path.join(os.path.dirname(__file__), 'static')

    app.router.add_routes(routes)
    app.add_routes([static('/static', static_path)])

    redis_url = app['redis_url']
    port = int(os.environ.get('PORT', '8080'))

    if redis_url:
        app.on_startup.append(lambda app: setup_aioredis(redis_url, app))
        app.on_cleanup.append(teardown_aioredis)
    else:
        app['cache'] = MemoryCache()

    app['fetcher'] = try_fetcher([
        fetch_danbooru_post(
            api_key=app['danbooru_api_key'],
            username=app['danbooru_username'],
        ),
        fetch_pixiv_url,
        fetch_http,
    ])

    run_app(app, port=port)
