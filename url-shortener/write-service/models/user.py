from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .url import URL


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    urls: List["URL"] = Relationship(back_populates="user")
