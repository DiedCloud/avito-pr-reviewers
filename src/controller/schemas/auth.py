from pydantic import BaseModel, Field


class UserRead(BaseModel):
    id: int
    login: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    login: str = Field(..., min_length=3, max_length=150)
    password: str = Field(..., min_length=6)
