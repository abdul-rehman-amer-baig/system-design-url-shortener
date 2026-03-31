from datetime import datetime, timezone

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis

from schemas import URLResolveResponse
from settings import settings
from storage import get_db, get_redis

router = APIRouter(prefix="/urls", tags=["urls"])


@router.get("/{short_code}", response_model=URLResolveResponse)
async def resolve_url(
    short_code: str,
    pool: asyncpg.Pool = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    cache_key = f"url:{short_code}"

    cached_url = await redis.get(cache_key)

    print("Cache key:", cache_key, "Cached URL:", cached_url)
    if cached_url:
        return URLResolveResponse(
            originalURL=cached_url,
            source="cache",
            servedBy=settings.INSTANCE_ID,
        )

    row = await pool.fetchrow(
        "SELECT original_url, expiration_time FROM urls WHERE short_code = $1",
        short_code,
    )
    print("Database row:", row)

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found",
        )

    if row["expiration_time"]:
        expiry = row["expiration_time"].replace(tzinfo=timezone.utc)
        if expiry < datetime.now(timezone.utc):
            await redis.delete(cache_key)
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Short URL has expired",
            )
        ttl = int((expiry - datetime.now(timezone.utc)).total_seconds())
    else:
        ttl = settings.CACHE_TTL

    await redis.setex(cache_key, ttl, row["original_url"])

    return URLResolveResponse(
        originalURL=row["original_url"],
        source="database",
        servedBy=settings.INSTANCE_ID,
    )
