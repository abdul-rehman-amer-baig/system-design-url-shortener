from pydantic import BaseModel


class URLResolveResponse(BaseModel):
    originalURL: str
    source: str       # "cache" or "database"
    servedBy: str     # which replica handled this request