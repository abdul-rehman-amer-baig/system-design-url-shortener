from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from storage import get_db
from models import User
from schemas import UserCreateRequest, UserResponse


router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.name == payload.name))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    user = User(name=payload.name)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserResponse(id=user.id, name=user.name)