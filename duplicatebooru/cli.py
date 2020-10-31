import logging
import os

from aiohttp.web import Application, run_app

from aiohttp_jinja2 import setup as setup_aiohttp_jinja2

from aioredis import create_redis_pool

from jinja2 import FileSystemLoader

from .cache import MemoryCache, RedisCache
from .web import routes


async def setup_aioredis(redis_url, app):
    redis = await create_redis_pool(redis_url)
    app['redis'] = redis
    app['cache'] = RedisCache(redis)


async def teardown_aioredis(app):
    redis = app['redis']

    redis.close()
    await redis.wait_closed()

    del app['cache']
    del app['redis']


def main():
    logging.basicConfig(level=logging.DEBUG)
    app = Application()

    setup_aiohttp_jinja2(
        app,
        loader=FileSystemLoader(os.path.dirname(__file__)),
    )

    app.router.add_routes(routes)

    redis_url = os.environ.get('REDIS_URL')
    port = int(os.environ.get('PORT', '8080'))

    if redis_url:
        app.on_startup.append(lambda app: setup_aioredis(redis_url, app))
        app.on_cleanup.append(teardown_aioredis)
    else:
        app['cache'] = MemoryCache()

    run_app(app, port=port)
