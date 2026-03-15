from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.dialects.postgresql import insert

from models import URL
from schemas import URLCreateRequest, URLCreateResponse
from services import sqids
from settings import settings
from storage import get_db, get_redis

router = APIRouter(prefix="/urls", tags=["urls"])

@router.post("", response_model=URLCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_short_url(
    payload: URLCreateRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    if payload.customAlias:
        short_code = payload.customAlias
    else:
        counter = await redis.incr("global:url_counter")
        short_code = sqids.generate_shortcode(counter)

    stmt = (
        insert(URL)
        .values(
            short_code=short_code,
            original_url=str(payload.originalURL),
            user_id=payload.userID,
            expiration_time=payload.expirationTime.replace(tzinfo=None) if payload.expirationTime else None,
        )
        .returning(URL.short_code)
    )

    try:
        result = await db.execute(stmt)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Alias '{short_code}' is already taken",
        )

    short_code = result.scalar_one()

    return URLCreateResponse(
        shortCode=short_code,
        shortURL=f"{settings.BASE_URL}/urls/{short_code}",
    )