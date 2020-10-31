from abc import ABCMeta, abstractmethod
from contextlib import asynccontextmanager
from json import dumps as json_dumps, loads as json_loads
from typing import Any, Iterator

from aioredis import Redis, create_redis_pool

from cachetools import LRUCache


class Cache(metaclass=ABCMeta):
    @abstractmethod
    async def get(self, url: str) -> Any:
        ...

    @abstractmethod
    async def set(self, url: str, data: Any) -> None:
        ...


class NoopCache(Cache):
    async def get(self, url: str) -> Any:
        return None

    async def set(self, url: str, data: Any) -> None:
        pass


class MemoryCache(Cache):
    def __init__(self, maxsize: int = 100):
        self.cache = LRUCache(maxsize=maxsize)

    async def get(self, url: str) -> Any:
        try:
            return self.cache[url]
        except KeyError:
            return None

    async def set(self, url: str, data: Any) -> None:
        self.cache[url] = data


class RedisCache(Cache):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, url: str) -> Any:
        data = await self.redis.get(url, encoding="utf-8")

        if data:
            return json_loads(data)

        return None

    async def set(self, url: str, data: Any) -> None:
        await self.redis.set(url, json_dumps(data))


@asynccontextmanager
async def redis(cls, url: str) -> Iterator[Redis]:
    redis = await create_redis_pool(url)

    try:
        yield redis
    finally:
        redis.close()
        await redis.wait_closed()
