from pydantic import BaseModel

class UserCreateRequest(BaseModel):
    name: str


class UserResponse(BaseModel):
    id: int
    name: str