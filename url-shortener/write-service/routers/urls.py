from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy import func
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
    if payload.expirationTime and payload.expirationTime < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Expiration time must be in the future.",
        )

    if payload.customAlias:
        short_code = payload.customAlias
    else:
        counter = await redis.incr("global:url_counter")
        short_code = sqids.generate_shortcode(counter)

    ins = insert(URL).values(
        short_code=short_code,
        original_url=str(payload.originalURL),
        user_id=payload.userID,
        expiration_time=payload.expirationTime.replace(tzinfo=None)
        if payload.expirationTime
        else None,
    )

    if payload.customAlias:
        stmt = ins.on_conflict_do_update(
            index_elements=["short_code"],
            set_={
                "original_url": ins.excluded.original_url,
                "user_id": ins.excluded.user_id,
                "expiration_time": ins.excluded.expiration_time,
                "created_at": func.now(),
            },
            where=URL.expiration_time < func.now(),
        ).returning(URL.short_code)
    else:
        stmt = ins.returning(URL.short_code)

    try:
        result = await db.execute(stmt)
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        orig = str(e.orig)
        if "ForeignKeyViolation" in orig or "foreign key" in orig.lower():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"User with id '{payload.userID}' does not exist.",
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Alias '{short_code}' is already taken.",
        )

    short_code = result.scalar_one_or_none()
    if short_code is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Alias '{payload.customAlias}' is already taken.",
        )

    # Evict any stale cache entry for this alias (no-op if it wasn't cached).
    if payload.customAlias:
        await redis.delete(f"url:{short_code}")

    return URLCreateResponse(
        shortCode=short_code,
        shortURL=f"{settings.BASE_URL}/urls/{short_code}",
    )
