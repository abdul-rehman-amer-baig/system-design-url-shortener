from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

if TYPE_CHECKING:
    from .user import User


class URL(SQLModel, table=True):
    __tablename__ = "urls"

    short_code: str = Field(primary_key=True, max_length=20)
    original_url: str
    user_id: int = Field(foreign_key="users.id", index=True)
    expiration_time: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="urls")
