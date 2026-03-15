from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl


class URLCreateRequest(BaseModel):
    originalURL: HttpUrl
    expirationTime: Optional[datetime] = None
    customAlias: Optional[str] = None
    userID: int


class URLCreateResponse(BaseModel):
    shortCode: str
    shortURL: HttpUrl