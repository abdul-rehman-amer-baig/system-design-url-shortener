import asyncpg
from redis.asyncio import Redis

from settings import settings

_pool: asyncpg.Pool = None


async def get_db() -> asyncpg.Pool:
    return _pool


async def get_redis():
    client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()


async def init_db():
    global _pool
    _pool = await asyncpg.create_pool(
        settings.DATABASE_URL,
        min_size=2,
        max_size=10,
    )


async def close_db():
    await _pool.close()